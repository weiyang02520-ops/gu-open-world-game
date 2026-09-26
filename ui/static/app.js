const $ = (id) => document.getElementById(id);
let currentState = null;

async function request(path, method = "GET", body = null) {
  const options = { method, headers: {} };
  if (body !== null) { options.headers["Content-Type"] = "application/json"; options.body = JSON.stringify(body); }
  const response = await fetch(path, options);
  const payload = await response.json();
  if (!response.ok || payload.ok === false) throw new Error(payload.error || "请求失败");
  return payload;
}

function esc(value) { return String(value ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c])); }
function toast(message, error = false) { const node = $("toast"); node.textContent = message || ""; node.style.color = error ? "#f0a093" : ""; }
function setText(id, value) { const node = $(id); if (node) node.textContent = value ?? ""; }

function render(state) {
  currentState = state;
  const player = state.player || {};
  const world = state.world || {};
  const activeSession = state.created === true;
  $("creation").classList.toggle("hidden", activeSession);
  $("game").classList.toggle("hidden", !activeSession);
  setText("day-label", `第 ${state.day || 1} 天`); setText("phase-label", state.phase || "上午");
  setText("player-name", player.name); setText("player-rank", player.rank); setText("origin-label", player.origin);
  setText("essence", `${player.primeval_essence ?? 0} / ${player.aptitude === "甲等" ? 120 : 100}`); setText("health", player.health ?? 0); setText("stones", player.yuan_stones ?? 0); setText("ap", `${state.action_points ?? player.action_points ?? 0} / 3`); setText("location", player.location); setText("weather", world.weather || "晴"); setText("location-title", player.location);
  const location = (state.locations || {})[player.location] || {}; setText("location-description", location.resource ? `这里可以关注：${location.resource}。` : "青茅山外围的一处落脚点。"); setText("danger", world.danger_level ?? 0); setText("resource-note", location.resource || "环境");
  const essenceMax = player.aptitude === "甲等" ? 120 : 100; $("essence-bar").style.width = `${Math.max(0, Math.min(100, (player.primeval_essence || 0) / essenceMax * 100))}%`; $("health-bar").style.width = `${Math.max(0, Math.min(100, player.health || 0))}%`;
  $("gu-list").innerHTML = (player.owned_gu || []).map((gu) => `<div class="gu-card"><div><strong>${esc(gu)}</strong><small>一转 · 持有</small></div><span class="tag">稳定</span></div>`).join("") || `<p class="muted">暂无蛊虫</p>`;
  const npcs = world.npcs || []; $("npc-list").innerHTML = npcs.map((npc) => `<div class="npc-card"><div><strong>${esc(npc.name)}</strong><small>${esc(npc.role)} · ${esc(npc.location)}</small></div><span class="muted">${esc(npc.status || npc.goal)}</span></div>`).join("") || `<p class="muted">暂无可见 NPC</p>`;
  const inventory = player.inventory || {}; $("inventory-list").innerHTML = Object.entries(inventory).filter(([, count]) => Number(count) > 0).map(([name, count]) => `<div class="inventory-item"><span>${esc(name)}</span><b>${count}</b></div>`).join("") || `<p class="muted">背包为空</p>`;
  const history = state.history || world.history || []; $("history-list").innerHTML = history.slice(-24).reverse().map((line) => `<li>${esc(line)}</li>`).join("") || `<li>世界尚未留下记录。</li>`;
  const pending = state.pending_event; $("event-panel").classList.toggle("hidden", !pending); if (pending) { setText("event-title", pending.title); setText("event-location", `${pending.location || player.location} · 危险 ${pending.danger}`); setText("event-danger", `危险 ${pending.danger}`); $("event-options").innerHTML = (pending.options || []).map((choice) => `<button data-choice="${esc(choice)}">${esc(choice)}</button>`).join(""); document.querySelectorAll("[data-choice]").forEach((button) => button.addEventListener("click", () => resolveEvent(button.dataset.choice))); }
  document.querySelectorAll("[data-action]").forEach((button) => { button.disabled = (state.action_points ?? 0) <= 0 || Boolean(pending); }); setText("action-status", `${state.action_points ?? 0} 点`);
}

async function refresh() { try { render(await request("/api/state")); } catch (error) { toast(error.message, true); } }
async function act(action) { try { const response = await request("/api/action", "POST", { action }); render(response.state); toast(response.result); } catch (error) { toast(error.message, true); } }
async function resolveEvent(choice) { try { const response = await request("/api/event/resolve", "POST", { choice }); render(response.state); toast(response.result); } catch (error) { toast(error.message, true); } }

document.addEventListener("DOMContentLoaded", () => {
  $("create-form").addEventListener("submit", async (event) => { event.preventDefault(); try { const response = await request("/api/create", "POST", { name: $("name-input").value, origin: $("origin-input").value, seed: Number($("seed-input").value) }); render(response.state); toast("角色已创建，第一天开始。"); } catch (error) { toast(error.message, true); } });
  document.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => act(button.dataset.action)));
  $("end-day").addEventListener("click", async () => { try { const response = await request("/api/end-day", "POST", {}); render(response.state); toast(response.result); } catch (error) { toast(error.message, true); } });
  $("save-game").addEventListener("click", async () => { try { const response = await request("/api/save", "POST", {}); toast(`已保存：${response.path}`); } catch (error) { toast(error.message, true); } });
  $("load-game").addEventListener("click", async () => { try { const response = await request("/api/load", "POST", {}); render(response.state); toast("存档已加载。"); } catch (error) { toast(error.message, true); } });
  refresh();
});
