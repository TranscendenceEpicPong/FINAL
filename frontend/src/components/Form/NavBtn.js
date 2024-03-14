import {html} from "../../html.js";
import { loadPage } from "../../router.js";

export default (props) => {
    const {href, style} = props;
    return {
        template: html`
            <button class="${style}">Accéder</button>
        `,
        handlers: [
            {
                selector: "button",
                event: "click",
                method: (e) => {
                    loadPage(href);
                }
            }
        ]
    };
}