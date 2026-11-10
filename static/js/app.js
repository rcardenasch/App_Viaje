
/* ==========================================
   MODALES
========================================== */

const abrirModal = (id) => {
    const modal = document.getElementById(id);

    if (!modal) return;

    modal.classList.remove("hidden");
    modal.classList.add("flex");

    document.body.classList.add("overflow-hidden");
};

const cerrarModal = (id) => {
    const modal = document.getElementById(id);

    if (!modal) return;

    modal.classList.add("hidden");
    modal.classList.remove("flex");

    document.body.classList.remove("overflow-hidden");
};

document.addEventListener("click", (event) => {

    const botonCerrar = event.target.closest("[data-modal-cerrar]");

    if (botonCerrar) {
        cerrarModal(botonCerrar.dataset.modalCerrar);
    }

    if (event.target.matches("[data-modal-abrir]")) {
        abrirModal(event.target.dataset.modalAbrir);
    }
});


/* ==========================================
   MENÚ MÓVIL
========================================== */

const menu = document.getElementById("menu-movil");

document.getElementById("btn-menu")?.addEventListener("click", () => {
    menu?.classList.toggle("hidden");
});


/* ==========================================
   MODO OSCURO
========================================== */

const aplicarTema = (tema) => {

    document.documentElement.classList.toggle(
        "dark",
        tema === "dark"
    );
};

const obtenerTema = () => {

    try {
        return localStorage.getItem("tema") || "light";
    } catch {
        return "light";
    }
};

aplicarTema(obtenerTema());

document.getElementById("btn-tema")?.addEventListener("click", () => {

    const nuevoTema =
        document.documentElement.classList.contains("dark")
            ? "light"
            : "dark";

    aplicarTema(nuevoTema);

    try {
        localStorage.setItem("tema", nuevoTema);
    } catch {
        // La interfaz continúa funcionando sin almacenamiento.
    }
});


/* ==========================================
   NOTIFICACIONES
========================================== */

const mostrarNotificacion = (mensaje, tipo = "success") => {

    const contenedor = document.getElementById("notificaciones");

    if (!contenedor) return;

    const colores = {
        success: "bg-success text-success-foreground",
        warning: "bg-warning text-warning-foreground",
        error: "bg-destructive text-white"
    };

    const elemento = document.createElement("div");

    elemento.className = `
        rounded-lg border p-4 shadow-lg
        ${colores[tipo] || colores.success}
    `;

    elemento.textContent = mensaje;

    contenedor.appendChild(elemento);

    // La eliminación se realiza de forma controlada.
    setTimeout(() => elemento.remove(), 4000);
};

window.mostrarNotificacion = mostrarNotificacion;
