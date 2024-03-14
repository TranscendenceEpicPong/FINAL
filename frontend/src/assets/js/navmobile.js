function initializeScript() {
    var mainContainer = document.body;
    var navContainer = document.getElementById("nav_container");
    var navMain = document.getElementById("nav_main");

    if (!navContainer || !navMain) {
        console.log("Initialization failed: nav elements not found");
        return; // Exit if the elements are not found
    }

    var startX, moveX;
    var isTouching = false; // Add a flag to monitor ongoing touch/mouse event

    // Function to handle the start of a touch or mouse event
    function handleStart(event) {
        if (isTouching) return; // Prevent multi-touch or touch+mouse events
        isTouching = true;
        startX = event.touches ? event.touches[0].clientX : event.clientX;
    }

    // Function to handle movement for touch or mouse on mainContainer
    function handleMoveMainContainer(event) {
        if (!isTouching) return; // Ignore if no valid start
        moveX = event.touches ? event.touches[0].clientX : event.clientX;
        // Open nav if swipe right
        if (moveX > startX + 150) {
            navContainer.classList.remove("d-none");
            reset();
        }
    }

    // Function to handle movement for touch or mouse on navContainer
    function handleMoveNavContainer(event) {
        if (!isTouching) return; // Ignore if no valid start
        moveX = event.touches ? event.touches[0].clientX : event.clientX;
        // Close nav if swipe left
        if (startX - moveX > 150) {
            navMain.classList.add("closed");
            setTimeout(function () {
                navContainer.classList.add("d-none");
                navMain.classList.remove("closed");
            }, 200);
            reset();
        }
    }

    // Reset start and move positions
    function reset() {
        startX = null;
        moveX = null;
        isTouching = false; // Reset touch flag
    }

    // Add event listeners for mainContainer
    mainContainer.addEventListener("touchstart", handleStart, { passive: true });
    mainContainer.addEventListener("touchmove", handleMoveMainContainer, { passive: true });
    mainContainer.addEventListener("touchend", reset);
    mainContainer.addEventListener("mousedown", handleStart);
    mainContainer.addEventListener("mousemove", handleMoveMainContainer);
    mainContainer.addEventListener("mouseup", reset);

    // Add event listeners for navContainer
    navContainer.addEventListener("touchstart", handleStart, { passive: true });
    navContainer.addEventListener("touchmove", handleMoveNavContainer, { passive: true });
    navContainer.addEventListener("touchend", reset);
    navContainer.addEventListener("mousedown", handleStart);
    navContainer.addEventListener("mousemove", handleMoveNavContainer);
    navContainer.addEventListener("mouseup", reset);

    console.log("Initialization completed: navmobile.js initialized");
}

var observer = new MutationObserver(function (mutations, obs) {
    var navContainerExists = document.getElementById("nav_container");
    var navMainExists = document.getElementById("nav_main");

    if (navContainerExists && navMainExists) {
        initializeScript();
    }
});

var config = { childList: true, subtree: true };
observer.observe(document.body, config);
