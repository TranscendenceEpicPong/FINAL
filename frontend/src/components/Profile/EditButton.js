import {html} from "../../html.js";
import {loadPage} from "../../router.js";

export default (props) => {
    return {
        template: html`
            <button
                class="btn btn-secondary btn-block btn-sm"
                type="button">
                <i class="fa fa-edit"></i>
            </button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: () => {
                    loadPage('/edit');
                }
            }
        ]
    };
}