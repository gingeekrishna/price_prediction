import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface PredictionResponse {
  predicted_price: number;
  message?: string;
}

interface VehicleRequest {
  vehicle_age: number;
  mileage: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, HttpClientModule],
  template: `
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="card shadow-lg">
            <div class="card-header bg-gradient text-white text-center py-4">
              <h1 class="mb-0">🚗 Vehicle Price Predictor</h1>
              <p class="mb-0 mt-2">Get accurate price predictions powered by AI</p>
            </div>
            <div class="card-body p-4">
              <form [formGroup]="predictionForm" (ngSubmit)="onSubmit()">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="age" class="form-label fw-bold">
                      <i class="fas fa-calendar-alt me-2"></i>Vehicle Age (years)
                    </label>
                    <input 
                      type="number" 
                      id="age"
                      class="form-control form-control-lg"
                      formControlName="age"
                      placeholder="e.g., 3"
                      min="0"
                      max="50">
                    <div *ngIf="predictionForm.get('age')?.invalid && predictionForm.get('age')?.touched" 
                         class="text-danger mt-1">
                      <small *ngIf="predictionForm.get('age')?.errors?.['required']">Vehicle age is required</small>
                      <small *ngIf="predictionForm.get('age')?.errors?.['min']">Age must be positive</small>
                    </div>
                  </div>
                  
                  <div class="col-md-6 mb-3">
                    <label for="mileage" class="form-label fw-bold">
                      <i class="fas fa-tachometer-alt me-2"></i>Mileage (km)
                    </label>
                    <input 
                      type="number" 
                      id="mileage"
                      class="form-control form-control-lg"
                      formControlName="mileage"
                      placeholder="e.g., 45000"
                      min="0">
                    <div *ngIf="predictionForm.get('mileage')?.invalid && predictionForm.get('mileage')?.touched" 
                         class="text-danger mt-1">
                      <small *ngIf="predictionForm.get('mileage')?.errors?.['required']">Mileage is required</small>
                      <small *ngIf="predictionForm.get('mileage')?.errors?.['min']">Mileage must be positive</small>
                    </div>
                  </div>
                </div>
                
                <div class="text-center mt-4">
                  <button 
                    type="submit" 
                    class="btn btn-primary btn-lg px-5"
                    [disabled]="predictionForm.invalid || isLoading">
                    <span *ngIf="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                    <i *ngIf="!isLoading" class="fas fa-calculator me-2"></i>
                    {{ isLoading ? 'Predicting...' : 'Predict Price' }}
                  </button>
                </div>
              </form>
              
              <!-- Error Alert -->
              <div *ngIf="errorMessage" class="alert alert-danger alert-dismissible fade show mt-4">
                <i class="fas fa-exclamation-triangle me-2"></i>
                {{ errorMessage }}
                <button type="button" class="btn-close" (click)="clearError()"></button>
              </div>
              
              <!-- Success Result -->
              <div *ngIf="predictionResult" class="result-card">
                <h3 class="mb-3">
                  <i class="fas fa-check-circle me-2"></i>Prediction Result
                </h3>
                <div class="price-display">
                  💰 {{ predictionResult | currency:'USD':'symbol':'1.2-2' }}
                </div>
                <p class="mb-0">Estimated Vehicle Price</p>
              </div>
              
              <!-- Additional Info -->
              <div class="mt-4 p-3 bg-light rounded">
                <h6 class="fw-bold mb-2">
                  <i class="fas fa-info-circle me-2"></i>How it works:
                </h6>
                <ul class="mb-0 small">
                  <li>Our AI model analyzes vehicle age and mileage</li>
                  <li>Market trends and historical data are considered</li>
                  <li>Predictions are based on comprehensive training data</li>
                  <li>Results provide estimated market value ranges</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .bg-gradient {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .card {
      border: none;
      border-radius: 15px;
    }
    
    .form-control:focus {
      border-color: #667eea;
      box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
    }
    
    .btn-primary {
      background: linear-gradient(45deg, #667eea, #764ba2);
      border: none;
      transition: all 0.3s ease;
    }
    
    .btn-primary:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .result-card {
      background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
      color: white;
      border-radius: 15px;
      animation: slideIn 0.5s ease-out;
    }
    
    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
    
    .price-display {
      font-size: 2.5rem;
      font-weight: bold;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    @media (max-width: 768px) {
      .price-display {
        font-size: 2rem;
      }
    }
  `]
})
export class AppComponent implements OnInit {
  title = 'Vehicle Price Predictor';
  predictionForm: FormGroup;
  predictionResult: number | null = null;
  errorMessage: string = '';
  isLoading: boolean = false;
  
  private apiUrl = 'http://localhost:8000'; // FastAPI backend URL

  constructor(
    private fb: FormBuilder,
    private http: HttpClient
  ) {
    this.predictionForm = this.fb.group({
      age: ['', [Validators.required, Validators.min(0)]],
      mileage: ['', [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    // Component initialization
  }

  onSubmit(): void {
    if (this.predictionForm.valid) {
      this.isLoading = true;
      this.errorMessage = '';
      this.predictionResult = null;

      const vehicleData: VehicleRequest = {
        vehicle_age: this.predictionForm.value.age,
        mileage: this.predictionForm.value.mileage
      };

      this.http.post<PredictionResponse>(`${this.apiUrl}/predict`, vehicleData)
        .subscribe({
          next: (response) => {
            this.predictionResult = response.predicted_price;
            this.isLoading = false;
          },
          error: (error) => {
            console.error('Prediction error:', error);
            this.errorMessage = error.error?.detail || 'Failed to get prediction. Please try again.';
            this.isLoading = false;
          }
        });
    } else {
      // Mark all fields as touched to show validation errors
      Object.keys(this.predictionForm.controls).forEach(key => {
        this.predictionForm.get(key)?.markAsTouched();
      });
    }
  }

  clearError(): void {
    this.errorMessage = '';
  }
}
