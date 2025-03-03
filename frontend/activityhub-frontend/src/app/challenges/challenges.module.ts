import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// This is a placeholder component - will be implemented in future stages
import { ChallengeListComponent } from './challenge-list/challenge-list.component';

const routes: Routes = [
  { path: '', component: ChallengeListComponent }
];

@NgModule({
  declarations: [
    ChallengeListComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class ChallengesModule { }
