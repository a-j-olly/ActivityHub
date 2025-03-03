import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// This is a placeholder component - will be implemented in future stages
import { SubmissionListComponent } from './submission-list/submission-list.component';

const routes: Routes = [
  { path: '', component: SubmissionListComponent }
];

@NgModule({
  declarations: [
    SubmissionListComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class SubmissionsModule { }
