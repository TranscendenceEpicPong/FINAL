import { html } from "../../html.js";
import { getData } from "../../store.js";
import { loadPage } from "../../router.js";
import {tournaments} from "../../api.js";

export default (props) => {
	const user = getData("auth.user");
	const { tournament: tournament_str } = props;
	const tournament = JSON.parse(tournament_str);

	const subscribedUsers = [];
	const pendingUsers = [];
	tournament.participants.forEach((participant) => {
		if (participant.is_active)
			subscribedUsers.push(participant.user)
		else
			pendingUsers.push(participant.user)
	});

	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100vh; overflow-y: auto">
					<menu-btn></menu-btn>
					<!-- New Section -->
					<div style="padding: 20px" class="d-block">
						<h2 style="color: white;">Tournament: ${tournament.name}</h2>

						${user.username === tournament.creator.user_name && html`
							<div style="max-width:300px;" class="mt-4">
								<button id="launch-tournament" class="btn btn-danger mt-2">Launch</button>
							</div>
						`}

					</div>
					<!-- Tournament Cards Container -->
					<div style="max-width:300px; margin: 20px;">
						<div
							style="background-color: #171a1d;border-radius: 10px;padding: 15px;">
							<h4 class="text-white mb-3">Users subscribed</h4>
							<div id="users_subscribed">
								<!--<div class="d-flex justify-content-between">
									<p class="text-white">test</p>
									<i
										class="fa fa-times text-danger pointer"
										onclick="remove_user()"></i>
								</div>-->
								${subscribedUsers.map((user) => html`
									<div class="d-flex justify-content-between">
										<p class="text-white">${user}</p>
									</div>
								`)}
							</div>
						</div>
						<div
							style="background-color: #171a1d;border-radius: 10px;padding: 15px;"
							class="mt-3">
							<h4 class="text-white mb-3">Users pending</h4>
							<div id="users_pending">
								${pendingUsers.map((user) => html`
									<div class="d-flex justify-content-between">
										<p class="text-white">${user}</p>
									</div>
								`)}
							</div>
						</div>
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#launch-tournament",
				event: "click",
				method: async function () {
                    try {
                        const res = await tournaments.launch(tournament.id);
                        console.log(res);
                        await loadPage()
                    } catch (e) {
                        console.error(e);
                        showToast(e.error ?? e);
                    }
                },
			},
		],
	};
};
