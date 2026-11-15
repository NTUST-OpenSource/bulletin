import "./styles/tokens.css";
import "./styles/base.css";
import { mount } from "svelte";
import App from "./App.svelte";
import NotFound from "./NotFound.svelte";
import { PATH } from "./article.svelte";

const target = document.getElementById("app");
if (!target) throw new Error("index.html has no #app");

// The server answers every path it does not know with this page; those get the not-found view.
const known = location.pathname === "/" || PATH.test(location.pathname);
export default known ? mount(App, { target }) : mount(NotFound, { target });
