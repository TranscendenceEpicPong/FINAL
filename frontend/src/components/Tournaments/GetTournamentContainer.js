import { html } from "../../html.js";
import { getData } from "../../store.js";
import { loadPage } from "../../router.js";
import { sendToSocket } from "../../utils/socket.js";

const States = {
	WAITING: 0,
	STARTED: 1,
	FINISHED: 2,
	RESERVED: 3,
};

export default (props) => {
	const current_user = getData("auth.user.username");
	const { tournament: tournament_str } = props;
	console.log(tournament_str);
	const tournament = JSON.parse(tournament_str);
	console.log(tournament.participants)
	const current_participant = tournament.participants.find(
		(participant) => participant.user === current_user
	);

	const userMatches = tournament.current_matches.map((match) => (
		[match.player1.username, match.player2.username]
			.includes(current_user) && match.state !== States.FINISHED ?
			match : undefined
	)).filter((match) => !!match);

	console.log(userMatches);
	console.log(tournament.matches);

	const matchesByPhase = tournament.matches.reduce((acc, match) => {
		if (!acc[match.phase])
			acc[match.phase] = [match]
		else
			acc[match.phase].push(match)
		return acc
	}, {});
	console.log(matchesByPhase)

	const phases = Object.keys(matchesByPhase)
	console.log(phases)

	function getStateTitle(state)
	{
		const states = [
			'Pas démarré',
			'En cours',
			'Terminé',
			'Résérvé'
		];
		return states[state];
	}

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
						<h2 style="color: white;">Tournament ${tournament.name}</h2>
					</div>
					<!-- Tournament Cards Container -->
					<div
						id="tournaments_container"
						class="d-cord-container"
						style="display: flex; flex-wrap: wrap; padding: 20px; gap: 20px;">
						
						${userMatches.map((match) => html`
							<div class="tournament-card">
								<h4 class="text-white">Play now</h4>
								<p style="color: #CCCCCC;">
									You will fight against
									${match.player1.username === current_user ?
										match.player2.alias :
										match.player1.alias}
								</p>
								<button class="btn btn-info btn-sm btn-start-tournament-game" data-username="${match.player1.username === current_user ? match.player2.alias :
										match.player1.username}">
									Join Game
								</button>
							</div>
						`)}
						

						${!current_participant.is_active && html`
							<div class="tournament-card">
								<h4 class="text-danger">Eliminated</h4>
								<p style="color: #CCCCCC;">
									You have been eliminated
								</p>
								<button class="btn btn-dark btn-sm" disabled>
									RIP 💀
								</button>
							</div>
						`}
						
						<table class="table table-striped table-dark mt-4">
							<thead>
								<tr>
									<th scope="col">Player 1</th>
									<th scope="col">Score</th>
									<th scope="col">Player 2</th>
									<th scope="col">Winner</th>
								</tr>
							</thead>
							
							<tbody>
								${phases.map((phase) => html`
									<tr><td>${phase}</td></tr>
									${matchesByPhase[phase].map((match) => html`
										<tr>
											<td>${match.player1.alias}</td>
											<td>${match.state !== States.FINISHED ?
												getStateTitle(match.state) :
												`${match.score_player1} - ${match.score_player2}`}
											</td>
											<td>${match.player2.alias}</td>
											<td>${match.winner ?? ' - '}</td>
										</tr>
									`)}
								`)}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		`,
		handlers: [
			{
				selector: '.btn-start-tournament-game',
				event: 'click',
				method: function(e)
				{
					console.log(e.target);
					sendToSocket({
						action: 'join-tournament-game',
						username: e.target.getAttribute('data-username'),
						tournamentId: tournament.id
					}, 'game');
				}
			},
			{
				selector: "#create",
				event: "click",
				method: function () {
					loadPage("/createtournament");
				},
			},
		],
	};
};
