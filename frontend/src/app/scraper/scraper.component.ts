import { Component, OnInit } from '@angular/core';
import { Link, LinkResult } from '../link';
import { ScraperService } from '../scraper.service';

@Component({
  selector: 'app-scraper',
  templateUrl: './scraper.component.html',
  styleUrls: ['./scraper.component.css']
})
export class ScraperComponent implements OnInit {
  error: any;
  link: Link = {url: ''};
  linkResult: LinkResult;
  resultUrl: string;
  spinner: boolean = false;

  constructor(private scraperService: ScraperService) { }

  ngOnInit() {
  }

  clear() {
    delete this.linkResult;
    delete this.error;
    this.spinner = false;
  }

  getLinkResult(url: string): void {
    this.clear();
    url = url.trim();
    if (!url) { return; }
    this.spinner = true;
    this.scraperService.getLinkResult({ url } as Link)
      .subscribe(linkResult => {
        this.linkResult = linkResult;
        this.resultUrl = url;
        this.spinner = false;
      }, error => {
          this.spinner = false;
          this.resultUrl = url;
          this.error = error
      });
  }
}
