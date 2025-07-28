/** @type {import('next').NextConfig} */
const nextConfig = {
    async rewrites() {
        return [{
                source: '/api/document/:path*',
                destination: 'http://upload-service:8000/api/documents/:path*',
            },
            {
                source: '/api/query/:path*',
                destination: 'http://query-service:8001/api/query/:path*',
            },
        ];
    },
};

module.exports = nextConfig;
