import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-children-list',
  template: `
    <div class="container">
      <h2>My Children</h2>
      <p>
        This component will display a list of your children and their
        activities.
      </p>
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
export class ChildrenListComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}
}
