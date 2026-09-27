// Focused event/state tests. Real persistence is tested by test_submission.py.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source = readFileSync(new URL('./static/core/cv-submit.js', import.meta.url), 'utf8');
class Element {
  handlers = {}; attributes = {}; children = []; disabled = false; hidden = true; textContent = '';
  addEventListener(name, fn) { this.handlers[name] = fn; }
  setAttribute(name, value) { this.attributes[name] = value; }
  append(...nodes) { this.children.push(...nodes); }
  focus() {}
}
function setup() {
  const form = new Element(), button = new Element(), checkbox = new Element(), feedback = new Element();
  form.dataset = {complete:'true'}; form.action = 'http://localhost/student/cv/tinjau/'; form.reportValidity = () => true;
  checkbox.checked = false;
  form.querySelector = selector => selector.includes('button') ? button : checkbox;
  let calls = 0, resolve, reject;
  const pending = new Promise((a,b) => { resolve=a; reject=b; });
  vm.runInNewContext(source, {
    document: {querySelector: selector => selector === '#cv-submit-form' ? form : feedback, createElement: () => new Element(), createTextNode: text => text},
    fetch: () => { calls++; return pending; }, FormData: class {}, Intl, Date, AbortController, setTimeout, clearTimeout,
  });
  return {form, button, checkbox, feedback, resolve, reject, calls:()=>calls, submit:()=>form.handlers.submit({preventDefault(){}})};
}
function response(status, body) { return {ok:status===200, headers:{get:()=> 'application/json'}, json:async()=>body}; }
let t=setup();
assert.equal(t.button.disabled, true);
await t.submit(); assert.equal(t.calls(),0);
t.checkbox.checked=true; t.checkbox.handlers.change(); assert.equal(t.button.disabled,false);
const first=t.submit(); await t.submit();
assert.equal(t.calls(),1); assert.equal(t.button.disabled,true); assert.equal(t.button.textContent,'Mengajukan CV...');
t.resolve(response(200,{ok:true, submitted_at:'2026-09-27T01:00:00Z',version:1})); await first;
assert.equal(t.button.textContent,'CV berhasil diajukan'); assert.equal(t.button.disabled,true);
await t.submit(); assert.equal(t.calls(),1);
console.log('PASS unchecked, loading, rapid double submit, server-confirmed success');
for (const status of [401,403,409,422,503]) {
  t=setup(); t.checkbox.checked=true; const p=t.submit();
  t.resolve(response(status,{ok:false,code:'validation',error:'Permintaan ditolak'})); await p;
  assert.equal(t.button.disabled,false); assert.equal(t.feedback.textContent,'Permintaan ditolak');
  assert.equal(t.button.textContent,'Ajukan CV ke LPK →');
}
console.log('PASS HTTP errors restore actionable state without success');
t=setup(); t.checkbox.checked=true; const failed=t.submit(); t.reject(new TypeError('network failed')); await failed;
assert.equal(t.button.disabled,false); assert.match(t.feedback.textContent,/Koneksi terputus/);
assert.equal(t.feedback.textContent.includes('berhasil diajukan'),false);
console.log('PASS network failure has uncertainty message and no false success');
