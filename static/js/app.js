/* Phase 4 progressive enhancements; core content remains usable without JS. */

function syncNavState() {
	const pathname = window.location.pathname.replace(/\/+$/, "") || "/";
	const links = document.querySelectorAll(".nav-link[href], .drawer-nav a[href]");
	links.forEach((link) => {
		const href = new URL(link.href, window.location.href).pathname.replace(/\/+$/, "") || "/";
		const isCurrent = href === pathname || (href !== "/" && pathname.startsWith(href));
		if (isCurrent) {
			link.setAttribute("aria-current", "page");
		} else {
			link.removeAttribute("aria-current");
		}
		link.classList.toggle("is-current", isCurrent);
	});
	document.querySelectorAll(".unit-sidebar a").forEach((link) => {
		const href = new URL(link.href, window.location.href).pathname.replace(/\/+$/, "") || "/";
		const isCurrent = href === pathname;
		link.classList.toggle("is-current", isCurrent);
		if (isCurrent) {
			link.setAttribute("aria-current", "page");
		} else {
			link.removeAttribute("aria-current");
		}
	});

	const toggle = document.getElementById("mobile-nav-toggle");
	if (toggle && toggle.checked) {
		toggle.checked = false;
	}

	const details = document.querySelectorAll("details");
	details.forEach((item) => {
		if (item.querySelector("a[aria-current='page']")) {
			item.setAttribute("open", "open");
		} else {
			item.removeAttribute("open");
		}
	});
}

function handlePageSwap(root = document) {
	syncNavState();
	const main = root.querySelector("main#main");
	const heading = main?.querySelector("h1") || root.querySelector("h1");
	if (window.location.pathname.startsWith("/business-units/") && heading) {
		document.title = `${heading.textContent.trim()} | Energicotel PLC`;
	}
	if (heading) {
		heading.setAttribute("tabindex", "-1");
		heading.focus({ preventScroll: true });
	}
	const title = document.title || "";
	const announcer = document.getElementById("page-announcer");
	if (announcer) {
		announcer.textContent = title;
	}
}

function initialisePage(root = document) {
	const progress = document.getElementById("page-progress");
	if (progress) {
		progress.classList.remove("scale-x-100");
		progress.classList.add("scale-x-0");
	}
	const navLinks = root.querySelectorAll("a[hx-get], .nav-link, .drawer-nav a");
	navLinks.forEach((link) => {
		if (!link.hasAttribute("hx-ext")) {
			link.setAttribute("hx-ext", "preload");
		}
		link.setAttribute("preload", "mouseover");
	});

	const hero = root.querySelector("[data-home-hero]");
	if (hero && !hero.dataset.initialised) {
		hero.dataset.initialised = "true";
		const slides = [...hero.querySelectorAll(".home-hero__slide")];
		const dots = hero.querySelector("[data-hero-dots]");
		let active = Math.max(0, slides.findIndex((slide) => slide.classList.contains("is-active")));
		const show = (index) => {
			active = (index + slides.length) % slides.length;
			slides.forEach((slide, position) => slide.classList.toggle("is-active", position === active));
			dots?.querySelectorAll("button").forEach((dot, position) => dot.setAttribute("aria-current", String(position === active)));
		};
		if (dots) {
			slides.forEach((slide, index) => {
				const dot = document.createElement("button");
				dot.type = "button";
				dot.setAttribute("aria-label", `Show slide ${index + 1}`);
				dot.addEventListener("click", () => show(index));
				dots.append(dot);
			});
		}
		hero.querySelector("[data-hero-prev]")?.addEventListener("click", () => show(active - 1));
		hero.querySelector("[data-hero-next]")?.addEventListener("click", () => show(active + 1));
		if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
			window.setInterval(() => show(active + 1), 7000);
		}
	}

	root.querySelectorAll("[data-image-slider]").forEach((slider) => {
		if (slider.dataset.initialised) return;
		slider.dataset.initialised = "true";
		const track = slider.querySelector(".image-slider__track");
		slider.querySelector("[data-slide-prev]")?.addEventListener("click", () => track.scrollBy({ left: -track.clientWidth * 0.72, behavior: "smooth" }));
		slider.querySelector("[data-slide-next]")?.addEventListener("click", () => track.scrollBy({ left: track.clientWidth * 0.72, behavior: "smooth" }));
	});

	syncNavState();
}

document.addEventListener("DOMContentLoaded", () => initialisePage());
document.addEventListener("htmx:load", (event) => initialisePage(event.detail.elt));
document.addEventListener("htmx:beforeRequest", () => {
	const progress = document.getElementById("page-progress");
	if (progress) {
		progress.classList.remove("scale-x-0");
		progress.classList.add("scale-x-100");
	}
});
document.addEventListener("htmx:afterRequest", () => {
	const progress = document.getElementById("page-progress");
	if (progress) {
		progress.classList.remove("scale-x-100");
		progress.classList.add("scale-x-0");
	}
});
document.addEventListener("htmx:afterSwap", (event) => handlePageSwap(event.detail.target || document));
document.addEventListener("htmx:afterSettle", () => {
	syncNavState();
	if (window.location.pathname.startsWith("/business-units/")) {
		const heading = document.querySelector("#unit-content h1");
		if (heading) {
			document.title = `${heading.textContent.trim()} | Energicotel PLC`;
		}
	}
});
document.addEventListener("htmx:responseError", () => {
	window.location.reload();
});

document.addEventListener("click", (event) => {
	const link = event.target.closest("a");
	if (!link) return;
	if (link.matches("[hx-get]")) {
		const drawer = document.getElementById("mobile-nav-toggle");
		if (drawer && drawer.checked) {
			drawer.checked = false;
		}
	}
});

const announcer = document.getElementById("page-announcer");
if (!announcer) {
	const liveRegion = document.createElement("div");
	liveRegion.id = "page-announcer";
	liveRegion.setAttribute("aria-live", "polite");
	liveRegion.setAttribute("aria-atomic", "true");
	liveRegion.style.position = "absolute";
	liveRegion.style.width = "1px";
	liveRegion.style.height = "1px";
	liveRegion.style.padding = "0";
	liveRegion.style.margin = "-1px";
	liveRegion.style.overflow = "hidden";
	liveRegion.style.clip = "rect(0, 0, 0, 0)";
	liveRegion.style.whiteSpace = "nowrap";
	liveRegion.style.border = "0";
	document.body.appendChild(liveRegion);
}
