# Deployment

Deploy the backend as a container or Python service, set its environment variables in a secret manager, and expose it via HTTPS. Build the frontend with `VITE_API_URL` set to that HTTPS API. Configure backend CORS to the exact deployed frontend origin. Do not deploy a Bing key to the browser. Local container testing is available through `docker compose up --build`; set `VITE_API_URL` to the public API URL before a frontend production deployment.
