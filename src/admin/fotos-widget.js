/* Campo «Fotos» simplificado para o painel (Decap CMS) — pensado para telemóvel.
   - Botões grandes: tirar foto com a câmara ou escolher várias da galeria
   - Reduz as fotos no próprio aparelho antes de enviar (envio mais rápido)
   - Miniaturas com: passar para principal, mover, apagar */
(function () {
  if (!window.CMS || !window.h || !window.createClass) return;
  var h = window.h;

  var CSS = "\
.fw{font-family:inherit}\
.fw-btns{display:flex;gap:10px;flex-wrap:wrap;margin:6px 0 14px}\
.fw-btn{flex:1 1 200px;display:flex;align-items:center;justify-content:center;gap:8px;min-height:56px;padding:12px 16px;border-radius:10px;border:2px solid #d71f26;background:#d71f26;color:#fff;font-size:17px;font-weight:600;cursor:pointer}\
.fw-btn.sec{background:#fff;color:#d71f26}\
.fw-btn[disabled]{opacity:.5;cursor:wait}\
.fw-msg{margin:0 0 12px;padding:10px 12px;border-radius:8px;background:#eef6ff;color:#1d4fa3;font-size:15px}\
.fw-msg.err{background:#fdecec;color:#a21b1b}\
.fw-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}\
.fw-item{position:relative;border:2px solid #e2e4e6;border-radius:10px;overflow:hidden;background:#f3f4f5}\
.fw-item.main{border-color:#d71f26}\
.fw-item img{display:block;width:100%;aspect-ratio:4/3;object-fit:cover;background:#ddd}\
.fw-tag{position:absolute;top:6px;left:6px;background:#d71f26;color:#fff;font-size:12px;font-weight:700;padding:3px 8px;border-radius:20px}\
.fw-bar{display:flex}\
.fw-bar button{flex:1;min-height:44px;border:0;border-top:1px solid #e2e4e6;background:#fff;font-size:18px;cursor:pointer}\
.fw-bar button+button{border-left:1px solid #e2e4e6}\
.fw-bar button:disabled{color:#ccc;cursor:default}\
.fw-bar .del{color:#a21b1b}\
.fw-empty{padding:22px;text-align:center;color:#6b6f74;border:2px dashed #cfd3d7;border-radius:10px;font-size:15px}\
.fw-hint{color:#6b6f74;font-size:13px;margin-top:10px}\
@media (max-width:800px){\
[class*=EditorContainer],[class*=ToolbarContainer],[class*=AppMainContainer],[class*=AppHeaderContent]{min-width:0!important}\
[class*=ToolbarContainer]{flex-wrap:wrap;height:auto!important;padding:6px 4px}\
.fw-btn{flex-basis:100%}\
.fw-grid{grid-template-columns:repeat(2,1fr);gap:8px}\
}";
  var st = document.createElement("style"); st.textContent = CSS; document.head.appendChild(st);

  function slug(s) {
    return String(s || "foto").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "foto";
  }
  function toArr(v) { return !v ? [] : (v.toJS ? v.toJS() : Array.isArray(v) ? v.slice() : [v]); }

  // Reduz a foto (máx. 2000 px, JPEG 85%) — mantém o original se não for possível
  function shrink(file) {
    return new Promise(function (resolve) {
      if (!/^image\//.test(file.type) || !window.createImageBitmap) return resolve(file);
      createImageBitmap(file, { imageOrientation: "from-image" }).then(function (bmp) {
        var max = 2000, s = Math.min(1, max / Math.max(bmp.width, bmp.height));
        var c = document.createElement("canvas");
        c.width = Math.round(bmp.width * s); c.height = Math.round(bmp.height * s);
        c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
        c.toBlob(function (b) { resolve(b && b.size < file.size ? b : file); }, "image/jpeg", 0.85);
      }).catch(function () { resolve(file); });
    });
  }

  var Control = window.createClass({
    getInitialState: function () { return { busy: false, msg: "", err: false, local: {} }; },

    pasta: function () {
      var f = this.props.field;
      return (f && f.get && f.get("pasta")) || "/assets/fotos/uploads";
    },

    set: function (arr) { this.props.onChange(arr); },

    addFiles: function (list) {
      var self = this, files = Array.prototype.slice.call(list || []);
      if (!files.length) return;
      var entry = this.props.entry, data = entry && entry.get && entry.get("data");
      var base = slug(data && (data.get("modelo") || "")) || "foto";
      var total = files.length, done = 0, novos = [];
      self.setState({ busy: true, err: false, msg: "A preparar " + total + (total > 1 ? " fotos…" : " foto…") });
      var chain = Promise.resolve();
      files.forEach(function (f, i) {
        chain = chain.then(function () {
          return shrink(f).then(function (blob) {
            var ext = blob.type === "image/jpeg" ? "jpg" : (f.name.split(".").pop() || "jpg").toLowerCase();
            var name = base + "-" + Date.now().toString(36) + "-" + i + "." + ext;
            var file = new File([blob], name, { type: blob.type || f.type });
            self.setState({ msg: "A enviar foto " + (done + 1) + " de " + total + "…" });
            return Promise.resolve(self.props.onPersistMedia(file, { field: self.props.field })).then(function () {
              var path = self.pasta().replace(/\/$/, "") + "/" + name;
              var local = Object.assign({}, self.state.local); local[path] = URL.createObjectURL(blob);
              done++; novos.push(path);
              self.setState({ local: local });
              self.set(toArr(self.props.value).concat([path]));
            });
          });
        });
      });
      chain.then(function () {
        self.setState({ busy: false, err: false, msg: done + (done === 1 ? " foto adicionada." : " fotos adicionadas.") + " Não se esqueça de carregar em «Publicar» → «Publicar agora»." });
      }).catch(function (e) {
        console.error(e);
        self.setState({ busy: false, err: true, msg: "Não foi possível enviar uma das fotos. Verifique a ligação à internet e tente de novo." });
      });
    },

    move: function (i, d) {
      var a = toArr(this.props.value), j = i + d;
      if (j < 0 || j >= a.length) return;
      var t = a[i]; a[i] = a[j]; a[j] = t; this.set(a);
    },
    principal: function (i) { var a = toArr(this.props.value); var t = a.splice(i, 1)[0]; a.unshift(t); this.set(a); },
    remove: function (i) {
      if (!window.confirm("Retirar esta foto?")) return;
      var a = toArr(this.props.value); a.splice(i, 1); this.set(a);
    },

    render: function () {
      var self = this, fotos = toArr(this.props.value), busy = this.state.busy;
      var cam = h("input", { type: "file", accept: "image/*", capture: "environment", style: { display: "none" },
        ref: function (el) { self.camEl = el; }, onChange: function (e) { self.addFiles(e.target.files); e.target.value = ""; } });
      var gal = h("input", { type: "file", accept: "image/*", multiple: true, style: { display: "none" },
        ref: function (el) { self.galEl = el; }, onChange: function (e) { self.addFiles(e.target.files); e.target.value = ""; } });

      var grid = fotos.length ? h("div", { className: "fw-grid" }, fotos.map(function (p, i) {
        var src = self.state.local[p] || p;
        return h("div", { key: p + i, className: "fw-item" + (i === 0 ? " main" : "") },
          h("img", { src: src, alt: "Foto " + (i + 1), loading: "lazy" }),
          i === 0 ? h("span", { className: "fw-tag" }, "Principal") : null,
          h("div", { className: "fw-bar" },
            h("button", { type: "button", title: "Mover para a esquerda", "aria-label": "Mover para a esquerda", disabled: i === 0, onClick: function () { self.move(i, -1); } }, "◀"),
            i === 0 ? null : h("button", { type: "button", title: "Tornar principal", "aria-label": "Tornar principal", onClick: function () { self.principal(i); } }, "★"),
            h("button", { type: "button", title: "Mover para a direita", "aria-label": "Mover para a direita", disabled: i === fotos.length - 1, onClick: function () { self.move(i, 1); } }, "▶"),
            h("button", { type: "button", className: "del", title: "Retirar foto", "aria-label": "Retirar foto", onClick: function () { self.remove(i); } }, "✕")
          ));
      })) : h("div", { className: "fw-empty" }, "Ainda não há fotos. Use os botões acima para adicionar.");

      return h("div", { className: "fw" },
        cam, gal,
        h("div", { className: "fw-btns" },
          h("button", { type: "button", className: "fw-btn", disabled: busy, onClick: function () { self.camEl && self.camEl.click(); } }, "📷 Tirar foto"),
          h("button", { type: "button", className: "fw-btn sec", disabled: busy, onClick: function () { self.galEl && self.galEl.click(); } }, "🖼️ Escolher fotos")
        ),
        this.state.msg ? h("p", { className: "fw-msg" + (this.state.err ? " err" : ""), role: "status" }, this.state.msg) : null,
        grid,
        h("p", { className: "fw-hint" }, "A foto marcada como «Principal» aparece primeiro no site. Use ★ para escolher outra, ◀ ▶ para mudar a ordem e ✕ para retirar.")
      );
    }
  });

  var Preview = window.createClass({
    render: function () {
      var a = toArr(this.props.value);
      return h("div", null, a.map(function (p, i) { return h("img", { key: i, src: p, style: { maxWidth: "160px", margin: "4px" } }); }));
    }
  });

  window.CMS.registerWidget("fotos", Control, Preview);
})();
