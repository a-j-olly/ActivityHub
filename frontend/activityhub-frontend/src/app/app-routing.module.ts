import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { HomeComponent } from './components/home/home.component';
import { AuthGuard } from './guards/auth.guard';

const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { 
    path: 'challenges', 
    loadChildren: () => import('./challenges/challenges.module').then(m => m.ChallengesModule),
    canActivate: [AuthGuard]
  },
  { 
    path: 'submissions', 
    loadChildren: () => import('./submissions/submissions.module').then(m => m.SubmissionsModule),
    canActivate: [AuthGuard],
    data: { role: 'child' }
  },
  { 
    path: 'children', 
    loadChildren: () => import('./children/children.module').then(m => m.ChildrenModule),
    canActivate: [AuthGuard],
    data: { role: 'parent' }
  },
  { 
    path: 'leaderboard', 
    loadChildren: () => import('./leaderboard/leaderboard.module').then(m => m.LeaderboardModule)
  },
  // Fallback route
  { path: '**', redirectTo: '/home' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }