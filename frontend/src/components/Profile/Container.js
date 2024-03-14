import { html } from "../../html.js";

export default (props) => {
    const {username, avatar, wins, loses, games} = props;
	console.log(games);
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100svh">
					<menu-btn></menu-btn>
					<div
                        id="profile_container"
                        class="d-cord-container"
                        style="overflow-y: auto; padding:20px;"
                    >
						<div
							class="list-group"
							style="margin: 25px; border-radius: 15px">
							<div class="card" style="width: 18rem;">
								<img src="${avatar}" class="card-img-top" alt="Avatar">
								<div class="card-body">
									<h5 class="card-title">${username}</h5>
									<p class="card-text">
										<ul>
											<li>Victoires: ${wins}</li>
											<li>Défaites: ${loses}</li>
										</ul>
									</p>
								</div>
							</div>
						</div>
						<p style="color: #aaaaaa;" class="${JSON.parse(games).length ? 'd-none': ''}">Aucune partie</p>
						<profile-game-history-container
							username="${username}"
							games="${games}"
							class="${!JSON.parse(games).length ? 'd-none': ''}"
						></profile-game-history-container>
					</div>
				</div>
			</div>
		`,
	};
};