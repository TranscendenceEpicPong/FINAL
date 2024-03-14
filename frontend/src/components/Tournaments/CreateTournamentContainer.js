import { html } from "../../html.js";
import { getData } from "../../store.js";
import { loadPage } from "../../router.js";
import {postData, tournaments} from "../../api.js";

export default (props) => {
	const user = getData("auth.user");
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100vh; overflow-y: auto">
					<menu-btn></menu-btn>
					<div
						class="shadow-lg mt-5 m-md-5 ml-auto mr-auto"
						style="background-color:#171a1d;max-width:500px;padding:20px;border-radius:10px;color:#dfdfdf;">
						<div
							style="display: flex; align-items: center; justify-content: space-between; gap: 20px;">
							<div>
								<h3 class="text-white">Create tournament</h3>
								<h6>
									Fill in the details to create a new
									tournament
								</h6>
							</div>
						</div>
						<br />
						<div>
							<div class="mt-3">
								<custom-input
									icon="fa fa-pencil"
									type="text"
									required="yes"
									id="create_tournament_name"
								>Tournament name</custom-input
								>
							</div>
							<div class="mt-3">
								<custom-input
									icon="fa fa-pencil"
									type="text"
									required="yes"
									value="${user.username}"
									id="create_tournament_alias"
								>My alias</custom-input
								>
							</div>
							<br />
							<div class="mt-3">
								<custom-input
									icon="fa fa-users"
									type="text"
									required="yes"
									id="create_tournament_users"
								>Add users</custom-input
								>
							</div>
							<div class="mt-3 text-right">
								<button
									class="btn btn-light btn-sm"
									id="add_user">
									Add
								</button>
							</div>
							<!-- user list -->
							<div class="mt-3" id="user_list"></div>
							<br />
							<div class="mt-3 d-flex justify-content-between">
								<button
									type="button"
									class="btn btn-light"
									id="cancel">
									Cancel
								</button>
								<button
									type="button"
									class="btn btn-primary"
									id="create">
									Create tournament
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#cancel",
				event: "click",
				method: function () {
					loadPage("/tournaments");
				},
			},
			{
				selector: "#add_user",
				event: "click",
				method: function () {
					const input = document.querySelector('input[id="create_tournament_users"]');
					const userList = document.querySelector("#user_list");
					const user = input.value.toLowerCase();
					// check if the user already exist
					const users = document.querySelectorAll("#user_list p");
					let userExist = false;
					users.forEach((u) => {
						if (u.innerText === user) {
							userExist = true;
						}
					});
					if (userExist) {
						return;
					}
					if (user) {
						userList.innerHTML += `
							<div class="d-flex justify-content-between">
								<p class="text-white">${user}</p>
								<i class="fa fa-times text-danger pointer" onclick='remove_user()'></i>
							</div>
						`;
						input.value = "";
					}
				},
			},
			{
				selector: "#create",
				event: "click",
				method: async function () {
					const users = document.querySelectorAll("#user_list p");
					const alias = document.querySelector("#create_tournament_alias input").value;
					const userList = [];
					users.forEach((user) => {
						userList.push(user.innerText);
					});
					const current_user = getData('auth.user.username')
					userList.push(current_user)
					console.log(userList)
					const reqBody = {
						name: document.querySelector('#create_tournament_name input').value,
						participants: userList.map((u) => (
							{ user: u, alias: u === current_user ? alias : undefined }
						)),
					}
					console.log(reqBody)
					try {
						const tournament = await tournaments.create(reqBody)
						console.log(tournament);
						await loadPage(`/tournaments/${tournament.id}`)
					} catch (e) {
						console.log(e)
						let err = ""
						for (const field in e) {
							err += `${field}:\n`
							for (const error of e[field]) {
								if (typeof error === "string") {
									err += `\t- ${error}\n`
								} else if (Array.isArray(error['user'])) {
									console.log(error)
									for (const user_error of error['user']) {
										err += `\t- ${error['user']}\n`
									}
								} else {
									console.error(error)
								}
							}
						}
						showToast(err)
					}
				},
			},
		],
	};
};
