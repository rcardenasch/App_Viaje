const estadoInicial = Object.freeze({
    asientos: [],
    seleccionados: []
});

const crearEstado = (
    estado,
    cambios
) => ({
    ...estado,
    ...cambios
});

let estado = estadoInicial;

const renderizarAsientos = (
    asientos
) => {

    const html = asientos
        .map(asiento => {

            const color =
                asiento.estado === "OCUPADO"
                ? "bg-red-500"
                : estado.seleccionados.includes(
                    asiento.id_asiento
                )
                ? "bg-blue-500"
                : "bg-green-500";

            return `
                <button
                    data-id="${asiento.id_asiento}"
                    ${asiento.estado === "OCUPADO"
                        ? "disabled"
                        : ""}
                    class="
                    ${color}
                    text-white
                    w-12
                    h-12
                    rounded">
                    ${asiento.numero_asiento}
                </button>
            `;
        })
        .join("");

    document
        .getElementById(
            "contenedor-asientos"
        )
        .innerHTML = `
            <div class="grid
                        grid-cols-4
                        gap-2">
                ${html}
            </div>
        `;
};

const seleccionarAsiento = (
    asientoId
) => {

    const existe =
        estado.seleccionados.includes(
            asientoId
        );

    const nuevosSeleccionados =
        existe
        ? estado.seleccionados.filter(
            x => x !== asientoId
        )
        : [
            ...estado.seleccionados,
            asientoId
        ];

    estado = crearEstado(
        estado,
        {
            seleccionados:
            nuevosSeleccionados
        }
    );

    renderizarAsientos(
        estado.asientos
    );
};

document.addEventListener(
    "click",
    e => {

        if(
            e.target.dataset.id
        ){

            seleccionarAsiento(
                Number(
                    e.target.dataset.id
                )
            );
        }
    }
);