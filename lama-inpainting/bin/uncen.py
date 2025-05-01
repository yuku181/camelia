from argparse import ArgumentParser
import os
import sys
import traceback

from saicinpainting.evaluation.utils import move_to_device
from saicinpainting.evaluation.data import ceil_modulo
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

import cv2
import hydra
import numpy as np
import torch
import tqdm
import yaml
from omegaconf import OmegaConf
from torch.utils.data._utils.collate import default_collate

from saicinpainting.training.data.datasets import make_default_val_dataset
from saicinpainting.training.data.datasets import make_default_train_dataloader
from saicinpainting.training.trainers import load_checkpoint
from saicinpainting.utils import register_debug_signal_handlers


from utils import find_regions
import torch.nn.functional as F

from saicinpainting.training.data.masks import get_mask_generator



def init_inpaint_model(model_path):

    train_config_path = os.path.join(model_path, 'config.yaml')
    with open(train_config_path, 'r') as f:
        train_config = OmegaConf.create(yaml.safe_load(f))

    train_config.training_model.predict_only = True
    train_config.visualizer.kind = 'noop'

    checkpoint_path = os.path.join(model_path, 
                                   'models', 
                                   'best.ckpt')
    model = load_checkpoint(train_config, checkpoint_path, strict=False, map_location='cpu')
    model.freeze()

    return model


def inpaint(model, image_orig, mask_orig):

    ker = np.ones((0,0), dtype=np.uint8)
    mask_orig = cv2.dilate(mask_orig[..., 0], kernel=ker, iterations=1)[..., None]

    use_mask_blend = True
    mask_blend = cv2.dilate(mask_orig[..., 0], kernel=ker, iterations=4)[..., None]
    if not use_mask_blend:
        mask_blend.fill(255)

    def proc(image_orig_p):
        image_p = image_orig_p.copy()
        if image_p.ndim == 3:
            image_p = np.transpose(image_p, (2, 0, 1))
        image_p = image_p.astype('float32') / 255
        return image_p

    image = proc(image_orig)
    mask  = proc(mask_orig)

    f = 4
    ker = np.ones((0,0), dtype=np.uint8)
    mask_orig2 = cv2.resize(255-mask_orig, (mask_orig.shape[1]//f, mask_orig.shape[0]//f), cv2.INTER_AREA)
    its = 36//f
    mask_orig2 = cv2.erode(mask_orig2, kernel=ker, iterations=its)
    regions = find_regions(np.dstack([mask_orig2, mask_orig2, mask_orig2]), (0, 0, 0)) 
    for i in range(len(regions)):
        regions[i] = np.array(list(regions[i])) * f


    out = image_orig.copy()
    out_orig = image_orig.copy()
    for pixel_set in regions:
        s = np.array(list(pixel_set))
        min_x = np.min(s[:, 1])
        min_y = np.min(s[:, 0])
        max_x = np.max(s[:, 1])
        max_y = np.max(s[:, 0])
        c_y, c_x = (max_y + min_y)//2, (max_x + min_x)//2
        r_h, r_w = max_y - min_y, max_x - min_x
        
        pix_cnt = (mask_orig[min_y:max_y, min_x:max_x, 0]/255).sum() 
        density = pix_cnt / (r_h * r_w)
        #print('HERE', pix_cnt, density)
        if r_h < 10 and r_w < 10 or pix_cnt < 100:
            continue

        const_pp = False
        if const_pp:
            pp = 256
        else:
            fac = 0.6
            pp = int(round(max(r_h, r_w)*fac))
            pp = ceil_modulo(pp, 8)
        #print(len(regions), pp)
        rsy, rey, rsx, rex = c_y-pp, c_y+pp, c_x-pp, c_x+pp
        #h, w = rey - rsy, rex - rsx
        pad = pp + 1

        region = F.pad(torch.from_numpy(image).unsqueeze(0), (pad,pad,pad,pad), mode='reflect')[:, :, pad+rsy:pad+rey, pad+rsx:pad+rex].numpy()[0]


        region_mask = F.pad(torch.from_numpy(mask).unsqueeze(0), (pad,pad,pad,pad), mode='reflect')[:, :, pad+rsy:pad+rey, pad+rsx:pad+rex].numpy()[0]

        batch_o = [dict(
                image=region,
                mask=region_mask,
                unpad_to_size=(pp*2,pp*2),
        )]
        batch = default_collate(batch_o)

        with torch.no_grad():
            batch = move_to_device(batch, model.device)
            batch['mask'] = (batch['mask'] > 0) * 1
            batch = model(batch)                    
            key = 'inpainted'
            cur_res = batch[key][0].permute(1, 2, 0).detach().cpu().numpy()
            unpad_to_size = batch.get('unpad_to_size', None)
            if unpad_to_size is not None:
                orig_height, orig_width = unpad_to_size
                cur_res = cur_res[:orig_height, :orig_width]

        cur_mask = mask_blend[max(0,rsy):rey, max(0,rsx):rex, :] / 255
        out[max(0,rsy):rey, max(0,rsx):rex, :] = (cur_res[max(0, -rsy):min(pp*2, pp*2-(rey-out.shape[0])), max(0, -rsx):min(pp*2, pp*2-(rex-out.shape[1])), :] * 255) * cur_mask    +   out[max(0,rsy):rey, max(0,rsx):rex, :] * (1-cur_mask) 
        cv2.rectangle(out_orig, (max(0,rsx),max(0,rsy)), (rex,rey), color=(0,0,255), thickness=2)

    out_orig[..., 0][mask_orig[..., 0] > 0.1] //= 2
    out_orig[..., 1][mask_orig[..., 0] > 0.1] += ((255 - out_orig[..., 1][mask_orig[..., 0] > 0.1])*0.25).astype(out_orig.dtype)
    out_orig[..., 2][mask_orig[..., 0] > 0.1] //= 2
    out_dbg = np.concatenate([out_orig, out], axis=1)

    return out, out_dbg


def main():

    parser = ArgumentParser()
    parser.add_argument('--in_dir', required=True, help='dir with input images')
    parser.add_argument('--mask_dir', required=True, help='dir with input masks')
    parser.add_argument('--out_dir', required=True, help='dir with inpainted outputs')
    parser.add_argument('--checkpoint', required=True, help='Checkpoint dir')
    parser.add_argument('--device', default='cuda:0', help='Device used for inference')
    parser.add_argument('--debug_dir', default=None, help='dir with debug output')
    args = parser.parse_args()

    model = init_inpaint_model(args.checkpoint)
    device = torch.device(args.device)
    model.to(device)

    if not os.path.exists(args.out_dir):
        os.makedirs(args.out_dir)
    if args.debug_dir and not os.path.exists(args.debug_dir):
        os.makedirs(args.debug_dir)

    files = os.listdir(args.in_dir)
    files = [f for f in files if f.endswith(('.png', ))]
    for img_f in files:
        in_file = os.path.join(args.in_dir, img_f)
        mask_file = os.path.join(args.mask_dir, img_f)
        print(in_file)

        img = cv2.cvtColor(cv2.imread(in_file), cv2.COLOR_BGR2RGB)
        mask = cv2.imread(mask_file)

        output, dbg = inpaint(model, img, mask)

        out_path = os.path.join(args.out_dir, img_f)
        cv2.imwrite(out_path, cv2.cvtColor(output, cv2.COLOR_BGR2RGB))

        if args.debug_dir:
            dbg_path = os.path.join(args.debug_dir, img_f)
            cv2.imwrite(dbg_path, cv2.cvtColor(dbg, cv2.COLOR_BGR2RGB))



if __name__ == '__main__':
    main()
