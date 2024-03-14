import { html } from "../../html.js";
import { getData } from "../../store.js";
import { loadPage } from "../../router.js";
import {tournaments} from "../../api.js";
import { isArray } from "../../utils.js";

const GoToButton = (tournament) => html`
	<!--p class="text-white">${tournament.id}</p-->
	<button data-tournament-id="${JSON.stringify(tournament.id)}"
			class="btn-go-to-tournament btn btn-info btn-sm"
	>
		Go to Tournament
	</button>
    <!--p class="text-white">${JSON.stringify(tournament.id)}</p>
    <code>${JSON.stringify(tournament)}</code>
    <p class="text-white">${JSON.stringify(tournament.id)}</p-->
`;

const RegisterButton = (tournament) => html`
	<button data-tournament-id="${JSON.stringify(tournament.id)}"
			class="btn-go-to-tournament btn btn-light btn-sm"
	>
		Register
	</button>
`;

const TournamentCard = (tournament) => html`
	<div class="tournament-card">
		<h4 class="text-white">${tournament.name}</h4>
		<p style="color: #CCCCCC;">Created by ${tournament.creator.user_name}</p>

		${tournament.participants.map(
			(p) => p.is_active ? p.user : undefined
		).includes(getData("auth.user.username")) ?
			GoToButton(tournament) :
			RegisterButton(tournament)
		}
	</div>
`;

export default async () => {
	let tournaments_list = await tournaments.list()
	if (!isArray(tournaments_list))
		tournaments_list = [];
	return {
		template: html`
			<div class="d-flex" style="background: #252a2f" id="mainContainer">
				<nav-container></nav-container>
				<div style="width: 100%; height: 100vh; overflow-y: auto">
					<menu-btn></menu-btn>
					<!-- New Section -->
					<div
						style="padding: 20px;"
						class="d-flex justify-content-between align-items-center">
						<h2 style="color: white;">Tournaments</h2>
						<button class="btn btn-light btn-sm" id="create">
							Create Tournament
						</button>
					</div>
					<!-- Tournament Cards Container -->
					<div
						id="tournaments_container"
						class="d-cord-container"
						style="display: flex; flex-wrap: wrap; padding: 20px; gap: 20px;"
					>
						${tournaments_list.map(tournament => TournamentCard(tournament))}
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: "#create",
				event: "click",
				method: function () {
					loadPage("/createtournament");
				},
			},
			{
				selector: "button.btn-go-to-tournament",
				event: "click",
				method: async function (event) {
					const id = event.target.dataset.tournamentId;
					await  loadPage(`/tournaments/${id}/`);
				}
			}
		],
	};
};
