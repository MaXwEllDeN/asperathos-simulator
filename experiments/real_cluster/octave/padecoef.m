## Copyright (C) 2014 Endre Kozma
##
## This file is part of Octave.
##
## Octave is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or (at
## your option) any later version.
##
## Octave is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Octave; see the file COPYING.  If not, see
## <http://www.gnu.org/licenses/>.

## -*- texinfo -*-
## @deftypefn  {Function File} {[@var{num}, @var{den}] =} padecoef (@var{T}, @var{N})
## Computes the @var{N}th-order Padé approximation of the continuous-time delay @var{T} in transfer function form.
## The row vectors num and den contain the numerator and denominator coefficients in descending powers of s.
## Both are @var{N}th-order polynomials. Both @var{N} and @var{T} must be non negative value.
##
## @tex
## The pad\'e approximation of $e^{-sT}$ is defined by the following equation
## $$ e^{-sT} \approx {P_n(s) \over Q_n(s)} $$
## Where both $P_n(s)$ and $Q_n(s)$ are $N^{th}$-order rational functions defined by the following expressions
## $$ P_n(s)=\sum_{k=0}^N {(2N - k)!N!\over (2N)!k!(N - k)!}(-sT)^k $$
## $$ Q_n(s) = P_n(-s) $$
## @end tex
## @ifnottex
## The padé approximation of exp(-sT) is defined by the following equation
## @group
## @example
##
##             Pn(s)
## exp(-sT) ≈ -------
##             Qn(s)
##
## @end example
## @end group
## Where both Pn(s) and Qn(s) are @var{N}th-order rational functions defined by the following expressions
## @group
## @example
##
##          N    (2N - k)!N!        k
## Pn(s) = SUM --------------- (-sT)
##         k=0 (2N)!k!(N - k)!
##
## Qn(s) = Pn(-s)
## @end example
## @end group
## @end ifnottex
##
## For example
## @group
## @example
## t = 0.1;
## n = 4;
## [num, den] = padecoef(t, n)
## @result{} num =
##
##       1.0000e-04  -2.0000e-02   1.8000e+00  -8.4000e+01   1.6800e+03
##
## @result{} den =
##
##       1.0000e-04   2.0000e-02   1.8000e+00   8.4000e+01   1.6800e+03
## @end example
## @end group
## @seealso{pade}
## @end deftypefn

function [num, den] = padecoef(T, N = 1)
  if ((T < 0) | (N < 0))
    error("T and N must be non negative.");
  endif
  N = round(N);
  k = N : -1 : 0;
  ##  num = factorial(2 * N - k) * factorial(N) / factorial(2 * N) ./ factorial(k) ./ factorial(N - k);
  num = prod(linspace((N - k + 1), (2 * N - k), N)', ones(1, N)) / prod(N + 1 : 2 * N) ./ factorial(k);
  num /= num(1);
  den = num .* (T .^ k);
  num .*= ((-T) .^ k);
endfunction

##
## For checking in Wolframalfa (look at Alternate forms -> more):
## PadeApproximant[Exp[x], {x, 0, {n, n}}]
##
