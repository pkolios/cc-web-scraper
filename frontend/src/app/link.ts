export class Link {
  url: string;
}

class Headings {
  h1: Array<string>;
  h2: Array<string>;
  h3: Array<string>;
  h4: Array<string>;
  h5: Array<string>;
  h6: Array<string>;
}

class InaccessibleLink {
  url: string;
}

export class LinkResult {
  external_links: Array<string>;
  headings: Headings;
  html_version: string;
  internal_links: Array<string>;
  inaccessible_links: Array<InaccessibleLink>;
  login_form: boolean;
  title: string;
}
