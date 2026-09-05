# Frontend

Requires Node.js 20+.

```powershell
npm.cmd install
Copy-Item .env.example .env
npm.cmd run dev
```

`VITE_API_URL` defaults to `http://127.0.0.1:8001`. Set it to a deployed HTTPS API URL for deployment. It must never contain credentials.

```powershell
npm.cmd run build
```

