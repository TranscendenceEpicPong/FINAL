import { html } from "../../html.js";
import { getData } from "../../store.js";
import { loadPage } from "../../router.js";
import {tournaments} from "../../api.js";

export default async ({ id }) => {
	const tournament = await tournaments.get(id);
	if (!tournament.id) {
		return html`404 Not found`;
	}

	const current_user = getData('auth.user.username');
	const isOwner = tournament.creator.user_name === current_user;
	const isSubscribed = tournament.participants.map(
		(p) => p.is_active ? p.user : undefined
	).includes(current_user);
	const isStarted = tournament.phase !== 'no';

	if (!isStarted)
	{
		if (!isSubscribed) return html`
			<subscribe-tournament-container
				tournament="${JSON.stringify(tournament)}"
			></subscribe-tournament-container>`;

		if (isOwner) return html`
			<manage-tournament-container
				tournament="${JSON.stringify(tournament)}"
				isOwner="${isOwner}"
				isStarted="${isStarted}"
			></manage-tournament-container>`;

		return html`
			<div
				style="background-color: #252a2f;height:100svh;color:white;display:flex;justify-content:center;align-items:center;flex-direction:column;"
			>
				<h1>Waiting for tournament to start</h1>

				<button type="button" 
					id="refresh-tournament" 
					onclick="document.refresh()"
					class="btn btn-secondary"
				>
					Refresh
				</button>
			</div>`;

	}

	return html`
			<get-tournament-container
				tournament="${JSON.stringify(tournament)}"
			></get-tournament-container>`;
};
