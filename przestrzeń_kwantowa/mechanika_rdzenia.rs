#[derive(Clone)]
struct SplątanieKwantowe {
    węzeł_źródłowy: Arc<Mutex<WęzełKwantowy>>,
    węzeł_celowy: Arc<Mutex<WęzełKwantowy>>,
    stan_entanglacji: f32,
    propagator: Box<dyn Fn(f32) -> f32>,
}

impl SplątanieKwantowe {
    fn aktualizuj_entanglacje(&mut self, delta_czasu: f64) {
        let mut źródło = self.węzeł_źródłowy.lock().unwrap();
        let mut cel = self.węzeł_celowy.lock().unwrap();
        
        let transfer = (self.propagator)(self.stan_entanglacji) * delta_czasu as f32;
        źródło.entropia -= transfer;
        cel.potencjał += transfer;
        
        self.stan_entanglacji = (self.stan_entanglacji + transfer).clamp(0.0, 1.0);
    }
}