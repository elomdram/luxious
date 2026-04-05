(function () {
    function activateTabFromHash() {
        const hash = window.location.hash;
        if (!hash) return;

        const tabLink = document.querySelector(
            `a[data-toggle="tab"][href="${hash}"]`
        );

        if (tabLink) {
            tabLink.click();
        }
    }

    // Au chargement
    document.addEventListener("DOMContentLoaded", activateTabFromHash);

    // Quand le hash change (passage d’un onglet à l’autre)
    window.addEventListener("hashchange", activateTabFromHash);
})();

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('a[data-toggle="tab"]').forEach(tab => {
        tab.addEventListener("shown.bs.tab", function (e) {
            history.replaceState(null, null, e.target.getAttribute("href"));
        });
    });
});

