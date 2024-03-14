import {html} from "../../html.js";
import { makeRequestBlock } from "../../utils/blocks.js";

export default (props) => {
    const {username} = props;
    return {
        template: html`
            <button
                class="btn btn-dark btn-sm"
                style="height: 30px; width: 30px">
                <i class="fas fa-ban"></i>
            </button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: () => {
                    makeRequestBlock(username, 'add');
                }
            }
        ]
    };
}