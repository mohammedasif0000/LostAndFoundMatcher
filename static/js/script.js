/* =========================================================
   LOST & FOUND — GLOBAL ITEM MODAL
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("itemModal");

    if (!modal) {
        return;
    }

    const overlay =
        document.getElementById("itemModalOverlay");

    const closeButton =
        document.getElementById("itemModalClose");

    const closeButtonBottom =
        document.getElementById("modalCloseButton");

    const cards =
        document.querySelectorAll(".item-card");


    const modalImage =
        document.getElementById("modalItemImage");

    const modalNoImage =
        document.getElementById("modalNoImage");

    const modalType =
        document.getElementById("modalItemType");

    const modalReturned =
        document.getElementById("modalReturned");

    const modalName =
        document.getElementById("modalItemName");

    const modalCategory =
        document.getElementById("modalCategory");

    const modalLocation =
        document.getElementById("modalLocation");

    const modalDate =
        document.getElementById("modalDate");

    const modalDescription =
        document.getElementById("modalDescription");

    const modalContact =
        document.getElementById("modalContact");


    /* =====================================================
       OPEN MODAL
    ===================================================== */

    function openModal(card) {

        const type =
            card.dataset.type || "";

        const name =
            card.dataset.name || "Unknown Item";

        const category =
            card.dataset.category || "Not specified";

        const location =
            card.dataset.location || "Not specified";

        const date =
            card.dataset.date || "Not specified";

        const description =
            card.dataset.description || "No description provided.";

        const contact =
            card.dataset.contact || "Contact information unavailable.";

        const image =
            card.dataset.image || "";

        const returned =
            card.dataset.returned;


        /* TYPE */

        modalType.textContent =
            type.toUpperCase();

        modalType.className =
            "item-modal-badge " + type;


        /* NAME */

        modalName.textContent = name;


        /* DETAILS */

        modalCategory.textContent =
            category;

        modalLocation.textContent =
            location;

        modalDate.textContent =
            date;

        modalDescription.textContent =
            description;

        modalContact.textContent =
            contact;


        /* IMAGE */

        if (image) {

            modalImage.src = image;
            modalImage.alt = name;

            modalImage.style.display =
                "block";

            modalNoImage.style.display =
                "none";

        } else {

            modalImage.src = "";

            modalImage.style.display =
                "none";

            modalNoImage.style.display =
                "flex";

        }


        /* RETURNED */

        if (
            returned === "1" ||
            returned === "true" ||
            returned === "True"
        ) {

            modalReturned.style.display =
                "inline-flex";

        } else {

            modalReturned.style.display =
                "none";

        }


        /* SHOW */

        modal.classList.add("open");

        modal.setAttribute(
            "aria-hidden",
            "false"
        );

        document.body.classList.add(
            "modal-open"
        );

    }


    /* =====================================================
       CLOSE MODAL
    ===================================================== */

    function closeModal() {

        modal.classList.remove("open");

        modal.setAttribute(
            "aria-hidden",
            "true"
        );

        document.body.classList.remove(
            "modal-open"
        );

    }


    /* =====================================================
       CARD CLICK
    ===================================================== */

    cards.forEach(function (card) {

        card.addEventListener(
            "click",
            function () {

                openModal(card);

            }
        );


        /* Keyboard accessibility */

        card.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();

                    openModal(card);

                }

            }
        );

    });


    /* =====================================================
       CLOSE EVENTS
    ===================================================== */

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeModal
        );

    }


    if (closeButtonBottom) {

        closeButtonBottom.addEventListener(
            "click",
            closeModal
        );

    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeModal
        );

    }


    /* ESC KEY */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal.classList.contains("open")
            ) {

                closeModal();

            }

        }
    );

});