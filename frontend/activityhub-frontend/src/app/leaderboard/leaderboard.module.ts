import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// This is a placeholder component - will be implemented in future stages
import { LeaderboardComponent } from './leaderboard.component';

const routes: Routes = [{ path: '', component: LeaderboardComponent }];

@NgModule({
  declarations: [LeaderboardComponent],
  imports: [CommonModule, RouterModule.forChild(routes)],
})
export class LeaderboardModule {}
