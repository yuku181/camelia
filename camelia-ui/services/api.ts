/**
 * Helper to access the API base URL from runtime configuration. The
 * `useRuntimeConfig` composable must be called within a Nuxt context (such as
 * inside a composable or Vue component). Wrapping the call in a function
 * ensures it executes at runtime rather than during module evaluation.
 */
function getApiBaseUrl(): string {
    return useRuntimeConfig().public.apiBaseUrl;
}

export interface ResultItem {
    filename: string;
    sessionId: string;
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
): Promise<{ sessionId: string }> {
    // Create form data with files
    const formData = new FormData();

    // Append each file to the form data
    files.forEach((file) => {
        formData.append('files', file);
    });

    // Add processing type
    formData.append('model_type', processingType);

    // Make API request to process images
    const API_BASE_URL = getApiBaseUrl();
    const response = await fetch(`${API_BASE_URL}/process`, {
        method: 'POST',
        body: formData
    });

    const data = (await response.json()) as ApiResponse;

    if (!response.ok) {
        throw new Error(data.error || 'Failed to process images');
    }

    if (!data.success || !data.session_id) {
        throw new Error('Invalid response from server');
    }

    return { sessionId: data.session_id };
}

/**
 * Check the status of a processing job
 */
export async function checkProcessingStatus(sessionId: string): Promise<{
    status: 'processing' | 'completed' | 'error';
    results?: Array<{ filename: string }>;
}> {
    const API_BASE_URL = getApiBaseUrl();
    const response = await fetch(`${API_BASE_URL}/status/${sessionId}`);

    if (!response.ok) {
        throw new Error('Failed to check processing status');
    }

    const data = await response.json();

    return {
        status: data.status,
        results: data.results
    };
}

/**
 * Stream logs from the processing job
 */
export function streamProcessingLogs(sessionId: string, onLog: (log: string) => void): () => void {
    const API_BASE_URL = getApiBaseUrl();
    const evtSource = new EventSource(`${API_BASE_URL}/logs/${sessionId}`);

    evtSource.onmessage = (event) => {
        if (event.data && event.data.trim()) {
            onLog(event.data);
            setTimeout(() => {
            }, 0);
        }
    };

    evtSource.onerror = () => {
        console.error('EventSource failed:', sessionId);
        evtSource.close();
    };

    return () => {
        evtSource.close();
    };
}

/**
 * Transform API results to the format for display
 */
export function transformResults(
    sessionId: string,
    results: Array<{ filename: string }>
): ResultItem[] {
    const API_BASE_URL = getApiBaseUrl();
    return results.map((result) => {
        return {
            filename: result.filename,
            sessionId,
            original: `${API_BASE_URL}/original/${result.filename}`,
            processed: `${API_BASE_URL}/results/${sessionId}/${result.filename}`
        };
    });
}

/**
 * Cancel a running processing job
 */
export async function cancelProcessingJob(sessionId: string): Promise<boolean> {
    try {
        const API_BASE_URL = getApiBaseUrl();
        const response = await fetch(`${API_BASE_URL}/cancel/${sessionId}`, {
            method: 'POST'
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to cancel processing');
        }

        const data = await response.json();
        return data.success === true;
    } catch (error) {
        console.error('Error cancelling job:', error);
        return false;
    }
}

/**
 * Send an edited mask to the server and get the new result
 */
export async function reinpaintImage(
    sessionId: string,
    filename: string,
    mask: Blob
): Promise<ResultItem> {
    const API_BASE_URL = getApiBaseUrl();
    const formData = new FormData();
    formData.append('mask', mask, 'mask.png');

    const response = await fetch(
        `${API_BASE_URL}/reinpaint/${sessionId}/${filename}`,
        {
            method: 'POST',
            body: formData
        }
    );

    const data = await response.json();

    if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to reinpaint image');
    }

    return {
        filename: data.filename,
        sessionId,
        original: `${API_BASE_URL}/original/${filename}`,
        processed: `${API_BASE_URL}/results/${sessionId}/${data.filename}`
    };
}
