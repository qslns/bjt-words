import { chromium } from 'playwright';
const b = await chromium.launch({ ...(process.env.PW_CHROME ? { executablePath: process.env.PW_CHROME } : {}), args: ['--autoplay-policy=no-user-gesture-required'] });
const c = await b.newContext({ viewport: {width:1180,height:820} });
const p = await c.newPage();
const errs = []; p.on('pageerror', e => errs.push(String(e)));
const audioReq = [];
p.on('response', r => { if (/\/audio\//.test(r.url())) audioReq.push(r.status() + ' ' + r.url().split('/bjt-words/')[1]); });
await p.goto('https://qslns.github.io/bjt-words/');
await p.click('[data-act="ltGo"] >> visible=true');
await p.waitForSelector('#v-light .lt-word');
for (let i = 0; i < 3; i++) { await p.click('[data-act="ltNext"] >> visible=true'); await p.waitForTimeout(700); }
await p.click('#v-light [data-act="sayS"]'); await p.waitForTimeout(1500);
const toast = await p.locator('#toast').textContent();
console.log('audio responses:', audioReq.slice(0, 12));
console.log('toast:', toast, '| errors:', errs);
await b.close();
