Set-Location apps\web
if (-not (Test-Path node_modules)) { npm install }
npm run dev
