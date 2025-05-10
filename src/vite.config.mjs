import { defineConfig } from "vite"
import { resolve } from "path"
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
    plugins: [
        tailwindcss()
    ],
    base: "/static/",
    build: {
        manifest: "manifest.json",
        outDir: resolve("./assets"),
        rollupOptions: {
            input: {
                test: resolve("./static/js/app.js"),
                css: resolve("./static/css/app.css"),
            }
        }
    }
})