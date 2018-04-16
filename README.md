# idcm_leverage_demo
leverage demo for idcm


# 杠杆交易演示

> 杠杆交易或保证金交易，是指以现有资产作为抵押，加倍借入资产进行交易，随着交易资产波动，收益也会根据杠杆倍数而加倍

现由杠杆类 **Leverage** 构建演示程序


```python
from Leverage import *
```

将每个交易对作为一个单独的杠杆账户，以 BTC/USDT 交易对为例


```python
leverage_demo = Leverage('btc', 'usdt')
```

该账户与其他账户分离，账户内有总资产、可借资产、可转出资产等变量

总资产 **total_asset** ：杠杆账户内资产的总和，包括可用资产+冻结资产，其中冻结资产一般指未成交单中的资产

初始总资产为 0


```python
print(leverage_demo.total_asset_1, 'BTC', ',', leverage_demo.total_asset_2, 'USDT')
```

    0 BTC , 0 USDT
    

若想针对此交易对进行杠杆交易，则应转入资产 **deposit** ：从其他账户通过资金划转转入杠杆账户里的币


```python
leverage_demo.deposit(0, 5000) # 此时举例转入5000 USDT
```

此时总资产即为转入资产


```python
print(leverage_demo.total_asset_1, 'BTC', ',', leverage_demo.total_asset_2, 'USDT')
```

    0 BTC , 5000 USDT
    

此时账户与现货交易账户完全相同，除了未成交挂单里冻结的资产外均可用于交易与转入转出，可转出资产为 **withdraw_available**


```python
print(leverage_demo.withdraw_available_1, 'BTC', ',', leverage_demo.withdraw_available_2, 'USDT')
```

    0 BTC , 5000.0 USDT
    

现在开始杠杆交易，通过类函数 **get_price()** 可得到此时 BTC/USDT 价格 **price** 为:


```python
leverage_demo.get_price()
print(leverage_demo.price)
```

    8141.21
    

> get_price() 默认通过币安的买一(bid)和卖一(ask)中间价取得价格，实际应用时应通过交易所 order book 取得，且始终取对价，即卖出取买一价，买入取卖一价

客户存入的资金作为保证金，可从平台借贷资产获得更多可交易资产，加倍交易，可获得的最高倍数为杠杆倍数 **max_lever**


```python
print(leverage_demo.max_lever, '倍')
```

    3 倍
    

亦即存入一块钱作为保证金可以借到两块钱，一块钱可以当成三块钱用
客户存入的两种资产均可作为保证金，其价值由当前价格互相计算，如上存入 0.5 BTC 与 1000 USDT 的情况，按照当前价格，总资产则相当于：

以 BTC 计价：


```python
leverage_demo.total_asset_1 + leverage_demo.total_asset_2 / leverage_demo.price
```




    0.614159320297597



或以 USDT 计价：


```python
leverage_demo.total_asset_1 * leverage_demo.price + leverage_demo.total_asset_2
```




    5000.0



据此可以计算 **calculate_cap** 可借的资产量 **borrow_available** ：


```python
leverage_demo.calculte_cap()
print(leverage_demo.borrow_available_1, 'BTC', '或者', leverage_demo.borrow_available_2, 'USDT')
```

    1.228318640595194 BTC 或者 10000.0 USDT
    

## 做多的情况

如果此时看多 BTC，即认为 BTC/USDT 价会上涨，则借 USDT 来买入 BTC，等待价格走高再以卖出 BTC 得到 USDT 归还，赚取差价

利用 loan 函数，计入借贷记录 all_loan 并同时开始计算利息 interest


```python
leverage_demo.loan(0, 8000) # 假设借 8000 USDT
leverage_demo.all_loan
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>loan_1</th>
      <th>loan_2</th>
      <th>interest_1</th>
      <th>interest_2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1.523850e+09</td>
      <td>0.0</td>
      <td>8000.0</td>
      <td>0.0</td>
      <td>8.0</td>
    </tr>
  </tbody>
</table>
</div>



日利率为 **interest_rate** ，即借出开始每 24 小时计算一次利息 **interest_grow**


```python
print('借BTC利率为', leverage_demo.interest_rate_1, '，借USDT利率为', leverage_demo.interest_rate_2)
```

    借BTC利率为 0.001 ，借USDT利率为 0.001
    

此时即可开始监控风险 **risk_monitor**


```python
leverage_demo.risk_monitor()
# 若客户借入资产和总资产的比值即风险率不随价格变化则没有平仓价，如上虽然借入了 USDT 但客户抵押品也是 USDT，所以风险率不随价格变化，没有平仓价
leverage_demo.risk
```




    Risk Rate         1.625
    STOP OUT PRICE     None
    Name: BTC/USDT, dtype: object




```python
# monitor 中可以看到客户当前总资产与剩余可借资产等情况，风险率低于转出风险率 **withdraw_risk_rate** 的情况下客户是不能转出资产的
leverage_demo.monitor
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Total</th>
      <th>Borrowed</th>
      <th>Borrow Available</th>
      <th>Withdraw Available</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>btc</th>
      <td>0</td>
      <td>0</td>
      <td>0.243698</td>
      <td>-0.368496</td>
    </tr>
    <tr>
      <th>usdt</th>
      <td>13000</td>
      <td>8000</td>
      <td>1984</td>
      <td>-3000</td>
    </tr>
  </tbody>
</table>
</div>


**risk** 中有风险率 **risk_rate** 与预估爆仓价 **stop_out_price**，其中

风险率=[(计价货币总资产-计价货币未还利息) × 最新成交价+(交易货币总资产-交易货币未还利息)]÷(计价货币借入资产 × 最新成交价+交易货币借入资产)

预估爆仓价格=(计价货币借入资产 × 爆仓风险率+计价货币未还利息-计价货币总资产)÷(交易货币总资产-交易货币未还利息-交易货币借入资产 × 爆仓风险率)

风险率是决定杠杆账户风险的指标，当风险率≥200%时，账户中多余的资产部分可通过资金划转转出；当风险率≤150%，风险率评估为风险，系统会给用户提示风险；当风险率≤110%，系统将强制平仓，并告知用户；三个阈值 **withdraw_risk_rate**，**margin_call_risk_rate**，**stop_out_risk_rate** 均可调

```python
print('风险率高于', leverage_demo.withdraw_risk_rate, '部分资产可取出，', \
      '低于', leverage_demo.margin_call_risk_rate, '将收到风险警告，', \
      '低于', leverage_demo.stop_out_risk_rate, '将被强制平仓')
```

    风险率高于 2 部分资产可取出， 低于 1.5 将收到风险警告， 低于 1.1 将被强制平仓
    

实际上风险率为 1 即 100% 时即用户总资产等于借入资产（计入利息后），如此时不平仓，进一步亏损则客户可能无力归还借入资产，设为 110% 则有部分安全垫，此时有平台接管客户账户，可以通过减仓等操作使风险率符合规定或直接完全平仓，应根据市场所受冲击能力决定安全垫即强平风险阈值

客户借入资产后开始以转入资产和借入资产即总资产交易 **trade**


```python
# 假设客户以转入与借入部分 USDT 共10000交易买入 BTC
leverage_demo.trade(0,10000)
leverage_demo.all_trade
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>trade_1</th>
      <th>trade_2</th>
      <th>fee_1</th>
      <th>fee_2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1.523850e+09</td>
      <td>0.0</td>
      <td>10000.0</td>
      <td>0.0</td>
      <td>10.0</td>
    </tr>
  </tbody>
</table>
</div>



之后客户持有资产与风险率等变化，通过 **risk_monitor** 监控：


```python
leverage_demo.risk_monitor()

```

当前资产情况为：


```python
leverage_demo.monitor
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Total</th>
      <th>Borrowed</th>
      <th>Borrow Available</th>
      <th>Withdraw Available</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>btc</th>
      <td>1.22694</td>
      <td>0</td>
      <td>0.241815</td>
      <td>-0.369243</td>
    </tr>
    <tr>
      <th>usdt</th>
      <td>3000</td>
      <td>8000</td>
      <td>1969.45</td>
      <td>-3007.28</td>
    </tr>
  </tbody>
</table>
</div>



风险情况为


```python
leverage_demo.risk
```




    Risk Rate            1.624090
    STOP OUT PRICE    4733.729297
    Name: BTC/USDT, dtype: float64



可以看到，客户刚交易后总资产量除了手续费外没有变化，所以风险率也几乎没有变化，但由于持有的两种资产量变了，则预估爆仓价跟随变化，此时预估爆仓价为：


```python
leverage_demo.stop_out_price
```




    4733.729297297297



即 BTC/USDT 价格如果不升反降，达到该价格，则风险率达到平仓风险率，账户有平台接管，强制减仓或平仓，即则由账户剩余资产卖出 BTC 得到 USDT 归还，如归还足额 USDT 后还有剩余，则返还到客户余额

## 做空的情况

如果看空 BTC，即认为 BTC/USDT 价会下跌，则借 BTC 来卖出得到 USDT，等待价格走低再以 USDT 买回 BTC 归还，赚取差价


```python
leverage_demo.__init__('btc', 'usdt')
leverage_demo.deposit(0, 5000)
```


```python
leverage_demo.loan(1.1, 0) # 假设借 1.1 个 BTC
leverage_demo.all_loan
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>loan_1</th>
      <th>loan_2</th>
      <th>interest_1</th>
      <th>interest_2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1.523850e+09</td>
      <td>1.1</td>
      <td>0.0</td>
      <td>0.0011</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



由于是以 USDT 作为抵押借入 BTC，则随着 BTC 价格上升，可能造成借入资产值上升而使得抵押资产不够，即此时风险率会随着价格变化而变化


```python
leverage_demo.risk_monitor()
leverage_demo.monitor
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Total</th>
      <th>Borrowed</th>
      <th>Borrow Available</th>
      <th>Withdraw Available</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>btc</th>
      <td>1.1</td>
      <td>1.1</td>
      <td>0.125633</td>
      <td>-0.486083</td>
    </tr>
    <tr>
      <th>usdt</th>
      <td>5000</td>
      <td>0</td>
      <td>1023.21</td>
      <td>-3958.87</td>
    </tr>
  </tbody>
</table>
</div>




```python
leverage_demo.risk
```




    Risk Rate             1.558106
    STOP OUT PRICE    45004.500450
    Name: BTC/USDT, dtype: float64



可见以一个资产为抵押借入另一种资产的情况，即使没有交易，也会有一个爆仓价，存在被强平的可能

此时看空 BTC，则应将借到的 BTC 卖出


```python
leverage_demo.trade(1.05, 0) # 假设卖出1.05个 BTC
```


```python
leverage_demo.all_trade
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>trade_1</th>
      <th>trade_2</th>
      <th>fee_1</th>
      <th>fee_2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1.523850e+09</td>
      <td>1.05</td>
      <td>0.0</td>
      <td>0.00105</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



此时资产情况为：


```python
leverage_demo.risk_monitor()
leverage_demo.monitor
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Total</th>
      <th>Borrowed</th>
      <th>Borrow Available</th>
      <th>Withdraw Available</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>btc</th>
      <td>0.05</td>
      <td>1.1</td>
      <td>0.123532</td>
      <td>-0.487134</td>
    </tr>
    <tr>
      <th>usdt</th>
      <td>13543.1</td>
      <td>0</td>
      <td>1006.1</td>
      <td>-3967.43</td>
    </tr>
  </tbody>
</table>
</div>



风险状况为：


```python
leverage_demo.risk
```




    Risk Rate             1.557151
    STOP OUT PRICE    11664.029880
    Name: BTC/USDT, dtype: float64



此时可见，价格如果不降反升，到达预估爆仓价：


```python
leverage_demo.stop_out_price
```




    11664.029879639995



则账户会被平台接管，强制平仓

## 多种资产作为保证金的情况

实际上，客户不只能转入一种资产，转入转出均可同时有两种资产，转入均为增加保证金，降低杠杆，增加可借与可取出资产；转出则相反


```python
leverage_demo.deposit(0.5, 1000) # 假设以上情况下，客户追加保证金，转入0.5个 BTC 与1000 USDT
leverage_demo.all_deposit
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>time</th>
      <th>deposit_1</th>
      <th>deposit_2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>1.523850e+09</td>
      <td>0.0</td>
      <td>5000.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1.523850e+09</td>
      <td>0.5</td>
      <td>1000.0</td>
    </tr>
  </tbody>
</table>
</div>



则此时资产情况为：


```python
leverage_demo.risk_monitor()
leverage_demo.monitor
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Total</th>
      <th>Borrowed</th>
      <th>Borrow Available</th>
      <th>Withdraw Available</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>btc</th>
      <td>0.55</td>
      <td>1.1</td>
      <td>1.3691</td>
      <td>0.13565</td>
    </tr>
    <tr>
      <th>usdt</th>
      <td>14543.1</td>
      <td>0</td>
      <td>11150.5</td>
      <td>1104.8</td>
    </tr>
  </tbody>
</table>
</div>



风险状况为：


```python
leverage_demo.risk
```




    Risk Rate             2.123319
    STOP OUT PRICE    21998.343811
    Name: BTC/USDT, dtype: float64



可见，由于客户追加了保证金，平仓线跟随上升，可借与可取资产也上升
