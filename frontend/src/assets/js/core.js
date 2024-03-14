function remove_user(tournament_id) {
	const user = event.target.parentElement;
	if (tournament_id) {
		// ajax request here to remove the user from the tournament
		const user_id = user.querySelector("p").innerText;
		console.log(user_id);
	}
	user.remove();
}

// # mainContainer on click, hide short-profile-menu

/* const mainContainer = document.getElementById("mainContainer");
mainContainer.addEventListener("click", (e) => {
	if (
		!e.target.closest("#short-profile-menu") &&
		!e.target.closest("#profile-menu")
	) {
		document.getElementById("short-profile-menu").classList.add("d-none");
	}
}); */

function showToast(message, duration = 3000) {
	let toastContainer = document.getElementById("toast-container");
	if (!toastContainer) {
		toastContainer = document.createElement("div");
		toastContainer.id = "toast-container";
		document.body.appendChild(toastContainer);
	}

	const toast = document.createElement("div");
	toast.className = "toast";
	toast.innerHTML = `
		<span>${message}</span>
		<i class="fas fa-times"></i>
	`;

	const closeIcon = toast.querySelector(".fa-times");
	closeIcon.addEventListener("click", () => {
		toast.classList.add("hide");
		setTimeout(() => {
			toastContainer.removeChild(toast);
		}, 600);
	});

	toastContainer.appendChild(toast);

	setTimeout(() => {
		toast.classList.add("hide");
		setTimeout(() => {
			if (toastContainer.contains(toast))
				toastContainer.removeChild(toast);
		}, 600);
	}, duration);
}