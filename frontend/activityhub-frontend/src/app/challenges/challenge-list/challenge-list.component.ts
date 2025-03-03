import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-challenge-list',
  template: `
    <div class="container">
      <h2>Challenges</h2>
      <p>This component will display a list of available challenges.</p>
      <p>It will be fully implemented in future development stages.</p>
    </div>
  `,
  styles: [
    `
      .container {
        padding: 20px;
        max-width: 1000px;
        margin: 0 auto;
      }
      h2 {
        color: #007bff;
        margin-bottom: 20px;
      }
    `,
  ],
  standalone: false,
})
export class ChallengeListComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}
}
