(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    // Проверяем что мы на странице Property (есть блок переводов)
    const firstBlock = document.querySelector("#id_translations-0-title");
    if (!firstBlock) return;

    // Находим блок с inline-переводами и вставляем кнопку перед ним
    const inlineGroup = document.querySelector(
      ".js-inline-admin-formset, [id*='translations-group'], .inline-group"
    );
    if (!inlineGroup) return;

    const btn = document.createElement("button");
    btn.type = "button";
    btn.innerHTML = "🌐 Перевести с русского на EN + KA";
    btn.style.cssText = `
      margin: 0 0 20px 0;
      padding: 10px 20px;
      background: #1e40af;
      color: #fff;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 8px;
    `;

    inlineGroup.parentNode.insertBefore(btn, inlineGroup);

    btn.addEventListener("click", async function () {
      // Берём текст из первого блока (RU, индекс 0)
      const ruTitle = document.querySelector("#id_translations-0-title")?.value?.trim();
      const ruDesc  = document.querySelector("#id_translations-0-description")?.value?.trim();
      const ruAddr  = document.querySelector("#id_translations-0-address_text")?.value?.trim();

      if (!ruTitle) {
        alert("Сначала заполните заголовок на русском языке (первый блок переводов).");
        return;
      }

      // Убеждаемся что в первом блоке выбран язык RU
      const lang0 = document.querySelector("#id_translations-0-language");
      if (lang0 && lang0.value !== "ru") {
        alert("Первый блок переводов должен быть на русском языке (RU).");
        return;
      }

      btn.textContent = "⏳ Переводим...";
      btn.disabled = true;

      // CSRF токен из cookie
      function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^|;) ?" + name + "=([^;]*)(;|$)"));
        return match ? match[2] : null;
      }

      async function translateField(text) {
        if (!text) return { en: "", ka: "" };
        const resp = await fetch("/api/translate/", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken"),
          },
          body: `text=${encodeURIComponent(text)}`,
        });
        if (!resp.ok) {
          const err = await resp.json();
          throw new Error(err.error || "Ошибка сервера");
        }
        return await resp.json();
      }

      try {
        // Переводим все три поля параллельно
        const [titleT, descT, addrT] = await Promise.all([
          translateField(ruTitle),
          translateField(ruDesc),
          translateField(ruAddr),
        ]);

        // Заполняем EN (индекс 1)
        const setField = (selector, value) => {
          const el = document.querySelector(selector);
          if (el) el.value = value;
        };

        setField("#id_translations-1-title",        titleT.en);
        setField("#id_translations-1-description",  descT.en);
        setField("#id_translations-1-address_text", addrT.en);

        // Заполняем KA (индекс 2)
        setField("#id_translations-2-title",        titleT.ka);
        setField("#id_translations-2-description",  descT.ka);
        setField("#id_translations-2-address_text", addrT.ka);

        // Проставляем языки в селекторах
        const lang1 = document.querySelector("#id_translations-1-language");
        const lang2 = document.querySelector("#id_translations-2-language");
        if (lang1) lang1.value = "en";
        if (lang2) lang2.value = "ka";

        btn.innerHTML = "✅ Переведено — проверьте и при необходимости отредактируйте";
        btn.style.background = "#15803d";

        setTimeout(() => {
          btn.innerHTML = "🌐 Перевести с русского на EN + KA";
          btn.style.background = "#1e40af";
          btn.disabled = false;
        }, 5000);

      } catch (err) {
        console.error(err);
        alert("Ошибка перевода: " + err.message);
        btn.innerHTML = "🌐 Перевести с русского на EN + KA";
        btn.style.background = "#1e40af";
        btn.disabled = false;
      }
    });
  });
})();