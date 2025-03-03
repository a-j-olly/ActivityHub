import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';

// This is a placeholder component - will be implemented in future stages
import { ChildrenListComponent } from './children-list/children-list.component';

const routes: Routes = [
  { path: '', component: ChildrenListComponent }
];

@NgModule({
  declarations: [
    ChildrenListComponent
  ],
  imports: [
    CommonModule,
    RouterModule.forChild(routes)
  ]
})
export class ChildrenModule { }