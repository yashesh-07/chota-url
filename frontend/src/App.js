import React, { useState } from 'react';
import axios from 'axios';
import { Link, Copy, CheckCircle, ExternalLink } from 'lucide-react';

function App() {
    const [longUrl, setLongUrl] = useState('');
    const [shortResponse, setShortResponse] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [copied, setCopied] = useState(false);

    // Use the env variable injected by Docker
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const handleShorten = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setShortResponse(null);
        setCopied(false);

        try {
            const response = await axios.post(`${API_BASE_URL}/shorten`, {
                url: longUrl
            });
            setShortResponse(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to shorten URL. Please check the link and try again.');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(shortResponse.short_url);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-6">
            <div className="max-w-2xl w-full space-y-8">
                <div className="text-center">
                    <div className="flex justify-center mb-4">
                        <Link size={48} className="text-blue-400" />
                    </div>
                    <h1 className="text-4xl font-bold tracking-tight">URL Shortener Pro</h1>
                    <p className="mt-2 text-slate-400">Fast, secure, and reliable link shortening at scale.</p>
                </div>

                <form onSubmit={handleShorten} className="space-y-4">
                    <div className="flex gap-2">
                        <input
                            type="url"
                            required
                            placeholder="Paste a long link (e.g., https://example.com/very/long/path)"
                            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                            value={longUrl}
                            onChange={(e) => setLongUrl(e.target.value)}
                        />
                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 px-6 py-3 rounded-lg font-semibold transition flex items-center gap-2"
                        >
                            {loading ? 'Shortening...' : 'Shorten'}
                        </button>
                    </div>
                    {error && <p className="text-red-400 text-sm">{error}</p>}
                </form>

                {shortResponse && (
                    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-300">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-slate-400">Your short link is ready:</span>
                            <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded">Base62 Generated</span>
                        </div>

                        <div className="flex items-center gap-3 p-3 bg-slate-900 rounded-lg border border-slate-700">
                            <span className="flex-1 font-mono text-blue-400 truncate">
                                {shortResponse.short_url}
                            </span>
                            <button
                                onClick={copyToClipboard}
                                className="p-2 hover:bg-slate-700 rounded-md transition text-slate-300"
                                title="Copy to clipboard"
                            >
                                {copied ? <CheckCircle size={20} className="text-green-400" /> : <Copy size={20} />}
                            </button>
                            <a
                                href={shortResponse.short_url}
                                target="_blank"
                                rel="noreferrer"
                                className="p-2 hover:bg-slate-700 rounded-md transition text-slate-300"
                            >
                                <ExternalLink size={20} />
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;