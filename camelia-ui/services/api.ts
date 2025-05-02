const API_BASE_URL: string = 'http://localhost:5000/api';

export interface ResultItem {
    filename: string;
    original: string;
    processed: string;
}

export interface ApiResponse {
    success: boolean;
    session_id: string;
    results: Array<{
        filename: string;
    }>;
    error?: string;
}

/**
 * Process images using the Camelia API
 */
export async function processImages(
    files: File[],
    processingType: 'black_bars' | 'white_bars' | 'transparent_black'
): Promise<ResultItem[]> {
    // Create form data with files
    const formData = new FormData();

    // Append each file to the form data
    files.forEach((file) => {
        formData.append('files', file);
    });

    // Add processing type
    formData.append('model_type', processingType);

    // Make API request to process images
    const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        body: formData
    });

    const data = (await response.json()) as ApiResponse;

    if (!response.ok) {
        throw new Error(data.error || 'Failed to process images');
    }

    if (!data.success || !data.session_id || !data.results || !data.results.length) {
        throw new Error('Invalid response from server');
    }

    const sessionId = data.session_id;

    // Transform API results to the format we need
    return data.results.map((result) => {
        return {
            filename: result.filename,
            original: `${API_BASE_URL}/original/${result.filename}`,
            processed: `${API_BASE_URL}/results/${sessionId}/${result.filename}`
        };
    });
}
