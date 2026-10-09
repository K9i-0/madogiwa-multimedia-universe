import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';
export default defineConfig({
  root:fileURLToPath(new URL('.',import.meta.url)),
  publicDir:fileURLToPath(new URL('../public',import.meta.url)),
  plugins:[react(), {name:'no-cloudflare-video',configureServer(server){
    server.middlewares.use((req,res,next)=>{
      const path=(req.url || '').split('?')[0];
      if(path==='/__video-audit'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(blocked));return;}
      if(path.startsWith('/media/') || /\.(mp4|webm|mov)$/i.test(path) || /^\/admin-api\/videos\/[^/]+\/preview$/.test(path)){
        blocked.push(path);res.statusCode=410;res.end('Video binary intentionally unavailable in YouTube-only preview');return;
      }
      if(path.startsWith("/admin-api/")){res.statusCode=405;res.end("Read-only preview: admin writes unavailable");return;}
      next();
    });
  }}],
  resolve:{alias:[{find:'@/routes/__root',replacement:fileURLToPath(new URL('./root-route.ts',import.meta.url))},{find:'@',replacement:fileURLToPath(new URL('../src',import.meta.url))}]},
  server:{host:'127.0.0.1',port:4176,strictPort:true,proxy:{'/inputs/':{target:'https://madogiwa.work',changeOrigin:true}}},
  build:{outDir:'dist',copyPublicDir:false}
});
const blocked:string[]=[];
