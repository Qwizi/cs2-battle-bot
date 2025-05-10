import 'vite/modulepreload-polyfill';
import htmx from 'htmx.org';


console.log("Hello from app.js");

window.htmx = htmx;
window.htmx.scrollBehavior = 'smooth';
window.htmx.config.globalViewTransitions = true;