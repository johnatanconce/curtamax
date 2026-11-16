/* Newsletter Curtamax · envio para a Brevo sem sair da página
   Para ligar: cole em ACTION a URL do formulário da Brevo
   (Brevo › Contatos › Formulários › seu formulário › Compartilhar › "action" do HTML incorporado).
   Os nomes dos campos (FIELDS) precisam ser iguais aos do formulário na Brevo. */
(function () {
  var ACTION = "https://2a930cc9.sibforms.com/v2/serve/MUIFAB-TopE_U96rrUSaGJN_wFbeG12VI8ZjJd2fAwI0czeRzFyqflIKnvwVwRQLNCwOcSeM4U8_lWBMhY4gDXWitNf-FB7NgT92rIQKTlNjpe9CTGYUP9LhIKyl92jlXFddR7JpPOZbJ82wC6fNxQ2k-tt1czrfoGqLLilVdMWSRYGhljPnbXFMV_PGg09hbTGw902TgdOcKpOLnw==";   // ex.: "https://xxxxxxxx.sibforms.com/serve/MUIFA..."
  var DOUBLE_OPTIN = false; // mude para true quando ativar o "E-mail duplo de confirmação" na Brevo
  if (!DOUBLE_OPTIN) document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".nl-small[data-doi]").forEach(function (e) { e.hidden = true; });
  });
  var FIELDS = { nome: "NOME", email: "EMAIL", empresa: "EMPRESA", optin: "OPT_IN" };

  function $(s, el) { return (el || document).querySelector(s); }
  function okEmail(v) { return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v); }

  function postIframe(url, data) {
    var name = "nl-frame-" + Date.now();
    var fr = document.createElement("iframe"); fr.name = name; fr.style.display = "none"; document.body.appendChild(fr);
    var f = document.createElement("form"); f.method = "POST"; f.action = url; f.target = name; f.style.display = "none";
    data.forEach(function (v, k) { var i = document.createElement("input"); i.type = "hidden"; i.name = k; i.value = v; f.appendChild(i); });
    document.body.appendChild(f); f.submit();
    setTimeout(function () { f.remove(); fr.remove(); }, 15000);
  }

  function setup(box) {
    var form = $("form", box), msg = $(".nl-msg", box), btn = $(".nl-btn", box);
    if (!form) return;
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      msg.textContent = ""; msg.className = "nl-msg";
      var nome = form.elements.nome, email = form.elements.email, emp = form.elements.empresa, ok = form.elements.optin, hp = form.elements.hp;
      [nome, email].forEach(function (i) { i.closest("label").classList.remove("bad"); });
      ok.closest("label").classList.remove("bad");
      var erro = "";
      if (!nome.value.trim()) { nome.closest("label").classList.add("bad"); erro = "Conte como podemos te chamar."; }
      if (!okEmail(email.value.trim())) { email.closest("label").classList.add("bad"); erro = erro || "Confira o e-mail: parece que falta alguma coisa."; }
      if (!ok.checked) { ok.closest("label").classList.add("bad"); erro = erro || "Marque a caixa de consentimento para assinar."; }
      if (erro) { msg.textContent = erro; msg.className = "nl-msg err"; return; }
      if (hp && hp.value) return; // robô
      if (!ACTION) { msg.textContent = "As inscrições abrem em breve. Enquanto isso, fale com a gente pelo WhatsApp."; msg.className = "nl-msg err"; return; }

      var data = new FormData();
      data.append(FIELDS.nome, nome.value.trim());
      data.append(FIELDS.email, email.value.trim());
      if (emp && emp.value.trim() && FIELDS.empresa) data.append(FIELDS.empresa, emp.value.trim());
      data.append(FIELDS.optin, "1");
      data.append("email_address_check", "");
      data.append("locale", "pt");

      btn.disabled = true;
      var done = function () {
        if (DOUBLE_OPTIN) {
          $(".nl-done .txt", box).textContent = "Enviamos um e-mail de confirmação para " + email.value.trim() + ". Clique no link dele para começar a receber.";
        } else {
          $(".nl-done b", box).textContent = "Inscrição feita!";
          $(".nl-done .txt", box).textContent = "A partir de agora, os artigos da Curtamax chegam em " + email.value.trim() + ".";
        }
        box.classList.add("sent"); btn.disabled = false;
      };
      var fail = function (t) { btn.disabled = false; msg.textContent = t || "Não conseguimos registrar agora. Tente de novo em instantes."; msg.className = "nl-msg err"; };
      var url = ACTION + (ACTION.indexOf("?") > -1 ? "&" : "?") + "isAjax=1";
      fetch(url, { method: "POST", body: data })
        .then(function (r) { return r.json().catch(function () { return { success: r.ok }; }); })
        .then(function (j) {
          if (j && j.success) done();
          else fail(j && j.errors && j.errors.message ? "Confira os dados: " + j.errors.message : null);
        })
        .catch(function () { postIframe(ACTION, data); done(); }); // bloqueio de CORS: envia pelo formulário oculto
    });
  }
  function init() { var b = document.querySelectorAll("[data-nl]"); for (var i = 0; i < b.length; i++) setup(b[i]); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
