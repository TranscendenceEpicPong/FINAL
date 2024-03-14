export function registerComponent(name, Component) {
	customElements.define(
		name,
		class extends HTMLElement {
			constructor() {
				super();
			}

			getAllAttributes() {
				const attributes = {};
				Object.values(this.attributes).forEach(
					(attr) => (attributes[attr.name] = attr.value)
				);
				return attributes;
			}

			connectedCallback() {
				const attributes = {
					...this.getAllAttributes(),
					textContent: this.textContent || "",
				};

				(async () => {
					const component = await Component(attributes)
					const template = component.template.content;

					this.innerHTML = ""
					this.appendChild(template.cloneNode(true));

					this.attachEventHandlers(component.handlers);
				})()
			}

			attachEventHandlers(handlers) {
				handlers?.forEach((handler) => {
					const elements = this.querySelectorAll(handler.selector);
					if (!elements.length) {
						console.warn(
							`No element found for selector ${handler.selector}`
						);
						return;
					}
					const options = Object.assign(
						{}, // new object
						{ // default options
							preventDefault: true,
						},
						handler.options || {}, // handler's options
					);
					elements.forEach((element) => {
						element.addEventListener(handler.event, (e) => {
							if (options.preventDefault) {
								e.preventDefault();
							}
							handler.method.bind(this)(e);
						});
					})
				});
			}
		}
	);
}
