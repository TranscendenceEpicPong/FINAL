import {html} from "../../html.js";
import { sendToSocket } from "../../utils/socket.js";

export default (props) => {
    const {mode, textContent} = props;
    return {
        template: html`
            <div class="container">
                <div>
                    <p style="color: #aaaaaa;">Joueur 1: w et s. Joueur 2: flèche haut, flèche bas</p>
                    <p style="color: #aaaaaa;" class="d-none">Votre couleur: <span id="your-color" style="color: transparent;">dsadsa</span></p>
                    <small id="help-start-game" style="color: #aaaaaa;">Appuyez sur une touche pour commencer<br></small>
                    <canvas id="canva-pong" width="800px" height="400px" style="background: black;"></canvas>
                    <div>
                        <button id="btn-start-game" class="btn btn-primary">Rejoindre / créer</button>
                    </div>
                </div>
            </div>
        `,
        handlers: [
            {
                selector: '#btn-start-game',
                event: 'click',
                method: () => {
                    sendToSocket({action: 'join'}, 'game');
                }
            }
        ]
    };
}
