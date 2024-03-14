import {html} from "../../html.js";
import { makeRequestFriend } from "../../utils/friends.js";

export default (props) => {
    const {username} = props;
    return {
        template: html`
            <button
                class="btn btn-danger btn-sm"
                style="
                aspect-ratio: 1 / 1;
                width: 30px;
                height: 30px;
            ">
                <i class="fas fa-times"></i>
            </button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: () => {
                    makeRequestFriend(username, 'delete');
                }
            }
        ]
    };
}