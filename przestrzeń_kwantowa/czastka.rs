use glam::Vec3;

#[derive(Clone)]
pub struct CzastkaKwantowa {
    pub pozycja: [f64; 4],
    pub prędkość: Vec3,
    pub żywotność: f32,
}

impl CzastkaKwantowa {
    pub fn aktualizuj(&mut self, delta_czasu: f64) {
        self.żywotność -= delta_czasu as f32 * 0.5;
        let prędkość_vec = self.prędkość * delta_czasu as f32;
        self.pozycja[0] += prędkość_vec.x as f64;
        self.pozycja[1] += prędkość_vec.y as f64;
        self.pozycja[2] += prędkość_vec.z as f64;
    }

    pub fn czy_aktywna(&self) -> bool {
        self.żywotność > 0.0
    }
}