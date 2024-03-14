import { html } from "../../../../html.js";
import { isCurrentUser } from "../../../../utils/profile.js";

export default (props) => {
    const {username, games} = props;
	return {
		template: html`
            <table class="table table-striped table-dark">
                <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col" class="d-none d-sm-table-cell">Joueur 1</th>
                        <th scope="col" class="d-none d-sm-table-cell">Joueur 2</th>
                        <th scope="col" class="d-sm-none">Adversaire</th>
                        <th scope="col" class="d-none d-sm-table-cell">Score joueur 1</th>
                        <th scope="col" class="d-none d-sm-table-cell">Score joueur 2</th>
                        <th scope="col">Gagnant</th>
                        <th scope="col">Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${
                        JSON.parse(games).map((game, index) => {
                            return html`
                                <tr class="bg-${game.winner === username ? 'success' : 'danger'}">
                                    <th scope="row">${index + 1}</th>
                                    <td class="d-none d-sm-table-cell">${game.player1}</td>
                                    <td class="d-none d-sm-table-cell">${game.player2}</td>
                                    <td class="d-sm-none">${isCurrentUser(game.player1) ? game.player2 : game.player1}</td>
                                    <td class="d-none d-sm-table-cell">${`${game.score_player1}`}</td>
                                    <td class="d-none d-sm-table-cell">${`${game.score_player2}`}</td>
                                    <td>${game.winner}</td>
                                    <td>${game.date}</td>
                                </tr>
                            `;
                        })
                    }
                </tbody>
            </table>
		`,
	};
};