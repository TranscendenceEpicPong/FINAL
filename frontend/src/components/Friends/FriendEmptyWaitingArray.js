import {html} from "../../html.js";

export default (props) => {
    return {
        template: html`
            <div
                class="d-flex justify-content-between align-items-center list-group-item">
                <div class="d-flex align-items-center">
                    <strong class="d-block">Aucune demande en attente</strong>
                </div>
            </div>
        `,
    };
}