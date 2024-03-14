import {html} from "../../html.js";
import {loadPage} from "../../router.js";

// Might enforce this later, now it's not really useful
// const Parameters = {
//     href: "string",
//     textContent: "string",
// }

export default (attributes) => {
    // We can use the function body to do some computations
    const test = "Hello World !";

    // We can destructure attributes to get needed attributes
    const {href, style, textContent} = attributes;

    const click = (event) => {
        // We can use the parameters passed to the component
        loadPage(href).then((page) => console.log(`Page loaded: `, page));
    };

    return {
        template: html`
            <a href="${href || '#'}" style="${style}">${textContent}</a>
        `,
        handlers: [
            {
                selector: "a",
                event: "click",
                method: click,
                options: { // [OPTIONAL] change default options
                    preventDefault: true, // default
                },
                // And we could add more, like additional parameters
                // ...
            }
        ],

    }
}