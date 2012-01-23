#lang racket

(define (scanl f acc lst)
  (cond
    [(empty? lst) empty]
    [else (let ([acc (f acc (first lst))])
            (cons acc (scanl f acc (rest lst))))]))

(define (water lst)
  (define (up lst)
    (scanl max 0 lst))
  (map - (map min (up x) (reverse (up (reverse lst)))) lst))

(define x (build-list 10 (lambda (_) (random 10))))
x
(water x)
